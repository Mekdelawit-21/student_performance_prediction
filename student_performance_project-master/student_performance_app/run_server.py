from app import app

if __name__ == '__main__':
    print("Starting Flask app...")
    print("Registered routes:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.rule} [{', '.join(rule.methods)}]")
    print("\nStarting server on http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=False)
