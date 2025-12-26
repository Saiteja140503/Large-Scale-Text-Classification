import os
import pickle
from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression

CATEGORIES = ['comp.graphics', 'sci.med', 'rec.sport.baseball', 'talk.politics.mideast']

def main():
    print("Fetching 20newsgroups dataset...")
    data = fetch_20newsgroups(subset='train', categories=CATEGORIES)
    
    print(f"Training samples: {len(data.data)}")
    print(f"Categories: {CATEGORIES}")
    
    print("Building ML pipeline...")
    clf = Pipeline([
        ('tfidf', TfidfVectorizer(max_features=5000)),
        ('logistic', LogisticRegression(max_iter=1000, random_state=42))
    ])
    
    print("Training model...")
    clf.fit(data.data, data.target)
    
    os.makedirs('../model', exist_ok=True)
    model_path = '../model/text_classifier.pkl'
    print(f"Saving model to {model_path}")
    with open(model_path, 'wb') as f:
        pickle.dump(clf, f)
    
    print(f"Model saved successfully!")
    print(f"Model size: {os.path.getsize(model_path) / 1024:.2f} KB")

if __name__ == '__main__':
    main()
