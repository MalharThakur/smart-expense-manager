import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

# Sample training data
data = [
    # Essential Expenses
    ("Bought groceries", "Essential"),
    ("Paid electricity bill", "Essential"),
    ("Mobile recharge", "Essential"),
    ("Monthly rent", "Essential"),
    ("Bought medicines", "Essential"),
    ("Water bill payment", "Essential"),
    ("Internet bill payment", "Essential"),
    ("Public transport fare (daily commute)", "Essential"),
    ("School fees for child", "Essential"),
    ("Loan EMI payment (home/car)", "Essential"),
    ("Fuel for essential travel (e.g., commute to work)", "Essential"),
    ("Health insurance premium", "Essential"),
    ("Car insurance premium", "Essential"),
    ("House maintenance (minor repairs)", "Essential"),
    ("Medical check-up", "Essential"),
    ("Childcare expenses", "Essential"),
    ("Home loan interest", "Essential"), # Can be separate from principal for tax purposes sometimes
    ("Car service (mandatory maintenance)", "Essential"),
    ("Property tax", "Essential"),
    ("Life insurance premium", "Essential"),
    ("Basic toiletries (soap, toothpaste)", "Essential"),
    ("Essential clothing replacement (e.g., work clothes)", "Essential"),

    # Non-Essential Expenses
    ("Netflix subscription", "Non-Essential"),
    ("Dinner at restaurant", "Non-Essential"),
    ("Shopping for clothes", "Non-Essential"),
    ("Gym membership", "Non-Essential"),
    ("Movie tickets", "Non-Essential"),
    ("Vacation travel expenses", "Non-Essential"),
    ("New smartphone purchase (upgrade)", "Non-Essential"),
    ("Concert tickets", "Non-Essential"),
    ("Eating out for lunch (non-work related)", "Non-Essential"),
    ("New video game", "Non-Essential"),
    ("Spa treatment", "Non-Essential"),
    ("Hobby supplies (e.g., art supplies, musical instruments)", "Non-Essential"),
    ("Expensive coffee from cafe", "Non-Essential"),
    ("Donation to charity (discretionary)", "Non-Essential"),
    ("New furniture (decorative)", "Non-Essential"),
    ("Gadget accessories (non-essential)", "Non-Essential"),
    ("Designer clothing purchase", "Non-Essential"),
    ("Party expenses", "Non-Essential"),
    ("Online course (for leisure)", "Non-Essential"),
    ("Magazine subscriptions", "Non-Essential"),
    ("Gifts for friends/family (non-mandatory)", "Non-Essential"),
    ("Ordering take-out food frequently", "Non-Essential"),
    ("Beauty salon visit (non-basic)", "Non-Essential"),
    ("Club membership (social)", "Non-Essential"),

    # Investment Expenses (or categories for money allocated to investments)
    ("Investment in stocks", "Investment"),
    ("Purchased mutual funds", "Investment"),
    ("Contribution to retirement fund (PPF, NPS)", "Investment"),
    ("Fixed Deposit (FD) creation", "Investment"),
    ("Purchased gold/silver", "Investment"),
    ("Real estate investment", "Investment"),
    ("SIP payment", "Investment"),

    # Miscellaneous Expenses
    ("Lost wallet (cash replacement)", "Miscellaneous"),
    ("Parking fine", "Miscellaneous"),
    ("Small vendor purchase (unplanned)", "Miscellaneous"),
    ("Accidental damage repair (small, unexpected)", "Miscellaneous"),
    ("Donation box contribution (small change)", "Miscellaneous"),
    ("Unidentified small withdrawal", "Miscellaneous"),
    ("Random purchase from street vendor", "Miscellaneous"),
    ("Paid for a lost library book", "Miscellaneous"),
    ("Impulse buy at checkout counter", "Miscellaneous"),
    ("Small change given to a beggar", "Miscellaneous"),
    ("One-off software license", "Miscellaneous"),
    ("Duplicate key cutting", "Miscellaneous"),
    ("Tyre puncture repair", "Miscellaneous"),
    ("Cleaning supplies (non-routine)", "Miscellaneous"),
    ("Batteries for remote", "Miscellaneous"),
    ("Newspapers/Magazines (single purchase)", "Miscellaneous"),
    ("Small gift for a colleague", "Miscellaneous"),
    ("Tips at a service center", "Miscellaneous"),
    ("Passport photo", "Miscellaneous"),
    ("Photocopying documents", "Miscellaneous"),
]
texts, labels = zip(*data)

# Train TF-IDF and model
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(texts)
model = MultinomialNB()
model.fit(X, labels)

# Save them
joblib.dump(model, "model.pkl")
joblib.dump(vectorizer, "vectorizer.pkl")

print("✅ model.pkl and vectorizer.pkl created!")
