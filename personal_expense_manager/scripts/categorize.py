def auto_categorize(description):
    desc = description.lower()

    if any(word in desc for word in ["rent", "house", "room", "mortgage", "housing loan", "emi"]):
        return "Essential", "Housing", "Rent/Mortgage"
    elif any(word in desc for word in ["grocery", "vegetable", "d-mart", "supermarket", "food store", "provisions",
                                       "rice", "milk", "bread", "eggs", "fruits", "meat", "fish", "oil", "sugar",
                                       "dairy", "staples", "farm"]): # Added more common grocery items
        return "Essential", "Food", "Grocery"
    elif any(word in desc for word in ["swiggy", "zomato", "restaurant", "cafe", "dining", "takeout", "eatery", "pizza", "burger", "coffee shop"]):
        return "Non-Essential", "Food", "Dining Out"
    elif any(word in desc for word in ["bus", "uber", "train", "auto", "taxi", "metro", "fuel", "petrol", "transport", "public transport", "commute"]):
        return "Essential", "Transport", "Commute"
    elif any(word in desc for word in ["movie", "netflix", "amazon prime", "hotstar", "subscription", "cinema", "concert", "event ticket", "gaming", "book", "magazine"]):
        return "Non-Essential", "Entertainment", "Leisure"
    elif any(word in desc for word in ["investment", "stocks", "mutual funds", "fd", "fixed deposit", "nps", "ppf", "real estate", "gold", "sip", "portfolio", "bonds"]):
        return "Investment", "Finance", "Portfolio"
    elif any(word in desc for word in ["electricity", "water bill", "internet bill", "phone bill", "mobile recharge", "utility", "gas bill"]):
        return "Essential", "Utilities", "Bills"
    elif any(word in desc for word in ["medicine", "doctor", "hospital", "pharmacy", "health", "clinic", "medical checkup", "insurance premium", "healthcare"]):
        return "Essential", "Health", "Medical"
    elif any(word in desc for word in ["clothes", "shopping", "shoes", "apparel", "fashion", "new outfit", "jewelry"]):
        return "Non-Essential", "Shopping", "Clothing/Personal"
    elif any(word in desc for word in ["gym", "membership", "spa", "salon", "personal care", "haircut", "beauty"]):
        return "Non-Essential", "Personal Care", "Wellness"
    elif any(word in desc for word in ["school fees", "tuition", "education", "course", "college", "university"]):
        return "Essential", "Education", "Fees"
    elif any(word in desc for word in ["loan emi", "credit card payment", "debt", "interest"]):
        return "Essential", "Finance", "Loan Repayment"
    elif any(word in desc for word in ["car service", "bike maintenance", "vehicle repair", "tyre", "automobile", "mechanic"]):
        return "Essential", "Transport", "Vehicle Maintenance"
    elif any(word in desc for word in ["lost wallet", "fine", "unplanned", "random purchase", "small change", "donation box", "batteries", "photocopy", "misc", "unexpected", "sundries"]):
        return "Miscellaneous", "Others", "Sundries"
    else:
        return "Uncategorized", "Others", "Uncategorized"