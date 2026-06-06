# email_classifier.py  —  Phase 10 (ML Email Classifier)
#
# PURPOSE:
#   Classify an incoming email into one of 5 categories BEFORE any AI extraction
#   happens. This is Tier 2 of the three-tier classification system:
#
#     Tier 1 (email_filters.py) — domain whitelist → only known client domains pass
#     Tier 2 (THIS FILE)        — ML model → label + confidence score
#     Tier 3 (future)           — LLM review for edge cases (confidence < 0.75)
#
# LABELS:
#   relevant     → manpower requests, RFQs, CV submissions — route to Groq AI extraction
#   irrelevant   → newsletters, system emails, greetings — drop silently
#   sensitive    → HR matters, medical, personal — flag for human review, no AI extraction
#   financial    → invoices, POs, payment requests — route to finance team
#   confidential → M&A, legal, board matters — escalate to management, no AI extraction
#
# HOW IT WORKS:
#   1. Combine subject + body into one text block (the main learning signal)
#   2. Add 3 extra numeric features: is this a known OFS/NOC domain? email length? has attachments?
#   3. TF-IDF converts text into a matrix of word-pair frequencies (unigrams + bigrams)
#   4. Logistic Regression learns the pattern for each label from training examples
#   5. At prediction time, it returns a label + confidence score (0.0 to 1.0)
#
# WHY LOGISTIC REGRESSION over Naive Bayes:
#   LR produces better-calibrated probabilities — "confidence 0.92" means the model
#   is genuinely 92% confident, which lets us reliably trigger Tier 3 at the 0.75 threshold.
#   NB probabilities tend to be overconfident or underconfident depending on feature correlation.
#
# RETRAINING:
#   Add new labeled rows to data/training_emails.csv, then run this file directly
#   (python email_classifier.py) to retrain and overwrite the saved model.

import sys
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from scipy.sparse import hstack, csr_matrix

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.metrics import classification_report

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Where training data lives
TRAINING_CSV = PROJECT_ROOT / "data" / "training_emails.csv"

# Where the trained model is saved (joblib binary)
# This file is created by train_classifier() and loaded by classify_email()
MODEL_PATH = PROJECT_ROOT / "data" / "email_classifier.joblib"

# Confidence below this threshold means the model is unsure — Tier 3 (LLM) should handle it
CONFIDENCE_THRESHOLD = 0.75

# All known OFS/NOC domain keywords — used as one feature signal
# A sender from one of these domains is more likely to be a genuine business email
KNOWN_INDUSTRY_DOMAINS = {
    "aramco.com", "saudiaramco.com", "adnoc.ae", "adnocdrilling.ae",
    "qatarenergy.com", "pdo.co.om", "kockw.com", "noc.ly", "basraoil.com",
    "halliburton.com", "slb.com", "schlumberger.com", "bakerhughes.com",
    "weatherford.com", "technipfmc.com", "petrofac.com", "shell.com",
    "bp.com", "totalenergies.com", "expro.com", "woodplc.com", "kbr.com",
    "worley.com", "saipem.com", "nov.com", "mcdermott.com",
}

# Labels in a fixed order — needed so the model's probability array
# lines up correctly with label names when we call predict_proba()
LABEL_NAMES = ["relevant", "irrelevant", "sensitive", "financial", "confidential"]


# ---------------------------------------------------------------------------
# FEATURE ENGINEERING
# ---------------------------------------------------------------------------

def _is_known_domain(sender_domain: str) -> int:
    """
    Return 1 if the sender domain is a known oil and gas company, 0 otherwise.
    This helps the model distinguish genuine business emails from newsletters or
    personal accounts even before reading the text.
    """
    if not sender_domain:
        return 0
    domain = str(sender_domain).lower().strip()
    # Check exact match AND subdomain match (e.g. mail.aramco.com → aramco.com)
    for known in KNOWN_INDUSTRY_DOMAINS:
        if domain == known or domain.endswith("." + known):
            return 1
    return 0


def _build_feature_row(subject: str, body: str, sender_domain: str,
                       has_attachments) -> tuple:
    """
    Convert one email into (combined_text, numeric_features_array).

    combined_text        — subject + body joined — fed into TF-IDF
    numeric_features     — [is_known_domain, email_length, has_attachments]
                           These capture signals that text alone misses.
                           For example, very short emails with attachments
                           and invoice keywords are likely financial.

    Returns a tuple (text_str, np.array of shape (3,))
    """
    combined_text = (str(subject) + " " + str(body)).strip()

    # email_length: normalised by 1000 so it's on a similar scale to other features
    # A typical manpower request is 200-500 words; a newsletter is often much longer
    email_length  = len(combined_text) / 1000.0

    numeric = np.array([
        _is_known_domain(sender_domain),
        email_length,
        1 if str(has_attachments).strip() in ("1", "True", "true", "yes", "Yes") else 0,
    ], dtype=float)

    return combined_text, numeric


def _build_feature_matrix(df: pd.DataFrame, tfidf: TfidfVectorizer = None,
                           fit: bool = False):
    """
    Build the full feature matrix from a DataFrame of emails.

    If fit=True, the TF-IDF vectorizer is trained on this data (training time).
    If fit=False, it uses an already-trained vectorizer (prediction time).

    Returns (feature_matrix, tfidf_vectorizer)
    The feature matrix is a scipy sparse matrix combining TF-IDF + numeric features.
    """
    texts   = []
    numerics = []

    for _, row in df.iterrows():
        text, num = _build_feature_row(
            row.get("subject", ""),
            row.get("body", ""),
            row.get("sender_domain", ""),
            row.get("has_attachments", 0),
        )
        texts.append(text)
        numerics.append(num)

    # TF-IDF: convert text into a sparse matrix of word/phrase frequencies
    # ngram_range=(1,2) means we consider single words AND two-word phrases
    # max_features=5000 keeps only the 5000 most useful terms (avoids overfitting)
    # sublinear_tf=True applies log scaling so very frequent words don't dominate
    if fit:
        tfidf = TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=5000,
            sublinear_tf=True,
            min_df=1,           # include terms that appear at least once
        )
        tfidf_matrix = tfidf.fit_transform(texts)
    else:
        tfidf_matrix = tfidf.transform(texts)

    # Stack numeric features alongside TF-IDF
    # numeric_matrix shape: (n_samples, 3) — converted to sparse for hstack compatibility
    numeric_matrix = csr_matrix(np.array(numerics))
    feature_matrix = hstack([tfidf_matrix, numeric_matrix])

    return feature_matrix, tfidf


# ---------------------------------------------------------------------------
# COLUMN NORMALISATION
# ---------------------------------------------------------------------------

def _normalise_training_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Map whatever column names the CSV has to the internal names that
    _build_feature_matrix() expects: body, sender_domain, has_attachments.

    This lets us accept both the original hand-crafted CSV format and the
    real-email CSV produced by fetch_all_raw.py (which has body_content,
    sender_email, and no has_attachments column).

    Mapping rules applied in order:
      body          <- body_content if present, else body_preview, else body
      sender_domain <- extracted from sender_email if sender_domain absent
      has_attachments <- defaults to "0" if the column is missing entirely
    """
    df = df.copy()

    # Body text: prefer full body_content over the short preview snippet
    if "body" not in df.columns:
        if "body_content" in df.columns:
            df["body"] = df["body_content"]
        elif "body_preview" in df.columns:
            df["body"] = df["body_preview"]
        else:
            df["body"] = ""

    # Sender domain: extract the part after @ from a full email address
    if "sender_domain" not in df.columns and "sender_email" in df.columns:
        df["sender_domain"] = (
            df["sender_email"]
            .str.split("@")
            .str[-1]
            .str.strip()
            .str.lower()
            .fillna("")
        )

    # Attachment flag: real-email CSVs don't carry this — default safely to 0
    if "has_attachments" not in df.columns:
        df["has_attachments"] = "0"

    return df


# ---------------------------------------------------------------------------
# TRAINING
# ---------------------------------------------------------------------------

def train_classifier(csv_path: Path = TRAINING_CSV,
                     model_path: Path = MODEL_PATH) -> dict:
    """
    Train the ML classifier from labeled email data and save it to disk.

    Accepts two CSV formats:
      - Original bootstrap format: label, subject, body, sender_domain, has_attachments
      - Real-email format:         label, subject, body_content, sender_email
        (produced by fetch_all_raw.py + manual labeling)
    Column differences are handled automatically by _normalise_training_df().

    Parameters:
        csv_path   — path to the labeled training CSV
        model_path — where to save the trained model

    Returns:
        dict with keys: accuracy, cv_mean, cv_std, n_samples, class_counts
    """
    print(f"\n[Phase 10] Training ML email classifier...")
    print(f"  Training data : {csv_path}")
    print(f"  Model output  : {model_path}")

    # --- Load training data ---
    try:
        df = pd.read_csv(csv_path, dtype=str).fillna("")
    except FileNotFoundError:
        print(f"  ERROR: Training CSV not found at {csv_path}")
        return {}

    if "label" not in df.columns or "subject" not in df.columns:
        print(f"  ERROR: CSV must have at least 'label' and 'subject' columns.")
        return {}

    # Normalise column names so _build_feature_matrix() always sees the same keys
    df = _normalise_training_df(df)

    print(f"\n  Loaded {len(df)} training samples")
    class_counts = df["label"].value_counts().to_dict()
    for label, count in sorted(class_counts.items()):
        print(f"    {label:<15} {count} examples")

    # --- Build features ---
    print("\n  Building TF-IDF features...")
    X, tfidf = _build_feature_matrix(df, fit=True)
    # .to_numpy() forces a plain NumPy array — avoids PyArrow-backed pandas Series issues
    y = df["label"].to_numpy(dtype=str)

    # --- Train the model ---
    # class_weight='balanced' handles imbalanced classes by upweighting rare labels
    # (financial, sensitive, confidential are rarer in real email streams than relevant/irrelevant)
    # max_iter=1000 ensures convergence for our multi-class problem
    model = LogisticRegression(
        class_weight="balanced",
        max_iter=1000,
        C=1.0,              # C=1.0 is a good default regularization strength
        solver="lbfgs",
    )

    # Cross-validation: split data into 3 folds, train on 2, test on 1 (repeat 3 times)
    # This gives us a reliable accuracy estimate even with a small dataset
    print("\n  Running 3-fold cross-validation...")
    cv_scores = cross_val_score(model, X, y, cv=3, scoring="accuracy")
    print(f"  CV accuracy: {cv_scores.mean():.2%} (+/- {cv_scores.std():.2%})")

    # Fit on the full dataset for the final saved model
    model.fit(X, y)

    # Full training set classification report — shows per-class precision/recall
    y_pred = model.predict(X)
    print(f"\n  Training set classification report:")
    print(classification_report(y, y_pred, zero_division=0))

    # --- Save everything needed for prediction ---
    # We save the tfidf vectorizer together with the model because prediction
    # must use exactly the same vocabulary that was built during training
    model_bundle = {
        "model":        model,
        "tfidf":        tfidf,
        "label_names":  LABEL_NAMES,
        "trained_on":   str(csv_path),
        "n_samples":    len(df),
        "cv_mean":      float(cv_scores.mean()),
    }

    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model_bundle, model_path)
    print(f"\n  Model saved to {model_path}")

    return {
        "accuracy":     float(cv_scores.mean()),
        "cv_mean":      float(cv_scores.mean()),
        "cv_std":       float(cv_scores.std()),
        "n_samples":    len(df),
        "class_counts": class_counts,
    }


# ---------------------------------------------------------------------------
# PREDICTION
# ---------------------------------------------------------------------------

def load_model(model_path: Path = MODEL_PATH) -> dict:
    """
    Load the saved model bundle from disk.

    Returns the bundle dict (with keys: model, tfidf, label_names, etc.)
    or None if the file does not exist (caller should then call train_classifier).
    """
    if not model_path.exists():
        return None
    try:
        return joblib.load(model_path)
    except Exception as e:
        print(f"  WARNING: Could not load model from {model_path}: {e}")
        return None


def classify_email(email_dict: dict, model_bundle: dict = None) -> dict:
    """
    Classify one email and return a label + confidence score.

    This is the main function called by run_parser.py for every incoming email.

    Parameters:
        email_dict   — standard email dict from email_reader.fetch_emails()
                       (needs keys: subject, body_content, sender_email, has_attachments)
        model_bundle — pre-loaded model bundle (pass this in run_parser.py to avoid
                       reloading from disk on every email; if None, loads from disk)

    Returns:
        dict with keys:
          label       — predicted class (e.g. "relevant")
          confidence  — probability for the predicted class (0.0 to 1.0)
          needs_review— True if confidence < CONFIDENCE_THRESHOLD (Tier 3 case)
          all_scores  — dict of {label: probability} for all 5 classes
    """
    # Load the model if caller didn't pass one in
    if model_bundle is None:
        model_bundle = load_model()

    if model_bundle is None:
        # No trained model exists yet — default to "relevant" so the pipeline doesn't break
        # This happens on the very first run before training. Train the model first.
        print("  WARNING: No ML model found. Run train_classifier() first.")
        print("  Defaulting to label=relevant so pipeline can continue.")
        return {
            "label":        "relevant",
            "confidence":   0.0,
            "needs_review": True,
            "all_scores":   {},
        }

    model  = model_bundle["model"]
    tfidf  = model_bundle["tfidf"]

    # Extract the fields we need from the email dict
    subject    = email_dict.get("subject", "")
    body       = email_dict.get("body_content", "")  # run_parser uses body_content
    sender     = email_dict.get("sender_email", "")
    has_attach = email_dict.get("has_attachments", False)

    # Extract just the domain from the full email address
    sender_domain = sender.split("@")[-1] if "@" in str(sender) else ""

    # Build a one-row DataFrame — same structure as training data
    one_row = pd.DataFrame([{
        "subject":         subject,
        "body":            body,
        "sender_domain":   sender_domain,
        "has_attachments": 1 if has_attach else 0,
    }])

    # Build feature matrix for this single email (fit=False = use existing vocabulary)
    X, _ = _build_feature_matrix(one_row, tfidf=tfidf, fit=False)

    # predict_proba returns an array of shape (1, n_classes)
    # Each value is the model's probability estimate for that class
    proba = model.predict_proba(X)[0]

    # Map probabilities back to label names
    # model.classes_ contains the labels in the order the model learned them
    all_scores = {
        label: round(float(prob), 4)
        for label, prob in zip(model.classes_, proba)
    }

    # The predicted label is simply the one with the highest probability
    best_label = max(all_scores, key=all_scores.get)
    confidence = all_scores[best_label]

    return {
        "label":        best_label,
        "confidence":   confidence,
        "needs_review": confidence < CONFIDENCE_THRESHOLD,
        "all_scores":   all_scores,
    }


# ---------------------------------------------------------------------------
# QUICK TEST / RETRAIN ENTRY POINT
# Run this file directly to train or retrain the classifier from the CSV:
#   python 05_classifier/email_classifier.py
# ---------------------------------------------------------------------------

if __name__ == "__main__":

    # Step 1 — Train (or retrain) the model from the CSV
    results = train_classifier()

    if not results:
        print("\n  Training failed. Check the CSV path and columns.")
        sys.exit(1)

    print(f"\n  Cross-validation accuracy : {results['cv_mean']:.2%}")
    print(f"  Training samples          : {results['n_samples']}")

    # Step 2 — Load the freshly trained model and test on sample emails
    bundle = load_model()

    test_emails = [
        {
            "subject":         "Manpower Request - 3 Drilling Engineers - KSA",
            "body_content":    "Dear Team, We require 3 Senior Drilling Engineers for Khurais Field. Mobilization July 2025. Rate 900 USD per day. IWCF required. Submit CVs by 15 June.",
            "sender_email":    "procurement@aramco.com",
            "has_attachments": False,
        },
        {
            "subject":         "Monthly Newsletter - Upstream Oil and Gas June 2025",
            "body_content":    "Welcome to the June edition of the Oil and Gas Monthly Newsletter. OPEC update, LNG outlook, digital transformation special feature. Click to read. Unsubscribe below.",
            "sender_email":    "news@oilandgasmagazine.com",
            "has_attachments": False,
        },
        {
            "subject":         "Invoice INV-2025-0501 for Manpower Services May 2025",
            "body_content":    "Please find attached invoice INV-2025-0501 for USD 36000 for manpower services in May 2025. Payment due in 30 days. Bank details as per attached.",
            "sender_email":    "accounts@bakerhughes.com",
            "has_attachments": True,
        },
        {
            "subject":         "Strictly Confidential - Partnership Proposal for Review",
            "body_content":    "This communication is strictly confidential. We would like to explore a strategic acquisition of the company. NDA attached for signature. Please do not discuss with anyone other than the named contact.",
            "sender_email":    "bd@expro.com",
            "has_attachments": True,
        },
        {
            "subject":         "Confidential HR Matter - Performance Disciplinary",
            "body_content":    "Dear Saral, I am writing about a sensitive disciplinary matter involving one of your placed candidates. The details are confidential and for management review only. Please call at your earliest convenience.",
            "sender_email":    "hr@halliburton.com",
            "has_attachments": False,
        },
        {
            "subject":         "Re: RFQ Abu Dhabi - Can you confirm availability?",
            "body_content":    "Hi Saral, following our call earlier, could you confirm whether the Toolpusher candidate is available for the 15 August start? Also please send his updated CV with certifications. Thanks",
            "sender_email":    "khalid@adnocdrilling.ae",
            "has_attachments": False,
        },
    ]

    print("\n" + "=" * 65)
    print("  CLASSIFICATION TEST RESULTS")
    print("=" * 65)

    for email in test_emails:
        result = classify_email(email, model_bundle=bundle)
        label      = result["label"]
        confidence = result["confidence"]
        flag       = " [Tier 3 review]" if result["needs_review"] else ""
        subject    = email["subject"][:50]
        print(f"\n  Subject   : {subject}")
        print(f"  Predicted : {label:<15} confidence {confidence:.2%}{flag}")

        # Show top 2 scores for transparency
        top2 = sorted(result["all_scores"].items(), key=lambda x: x[1], reverse=True)[:2]
        print(f"  Top scores: {top2[0][0]} {top2[0][1]:.2%}  |  {top2[1][0]} {top2[1][1]:.2%}")
