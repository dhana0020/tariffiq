from flask import Flask, request, jsonify, render_template
import pandas as pd

app = Flask(__name__)

# Load suppliers
# suppliers = pd.read_csv('./data/suppliers.csv')


@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')


@app.route('/suppliers', methods=['GET'])

def get_suppliers():
    suppliers = pd.read_csv('./data/suppliers.csv')
    """Return all suppliers"""
    return suppliers.to_dict(orient='records')


@app.route('/products', methods=['GET'])
def get_products():
    suppliers = pd.read_csv('./data/suppliers.csv')
    """Return unique product names"""
    return jsonify(sorted(suppliers["product"].str.strip().unique().tolist()))


@app.route('/countries', methods=['GET'])
def get_countries_for_product():
    """Return unique countries for a given product"""
    product = request.args.get('product')
    suppliers = pd.read_csv('./data/suppliers.csv')
    available_countries = suppliers[suppliers["product"].str.lower().str.strip() == product.lower().strip()]["country"].unique().tolist()
    return jsonify(available_countries)


@app.route('/impact', methods=['POST'])
def impact():
    """Calculate cost impact after applying tariff"""
    data = request.json
    product = data.get('product')
    country = data.get('country')
    new_tariff = data.get('new_tariff')
    if not all([product, country, new_tariff is not None]):
        return jsonify({"error": "Missing required fields"}), 400
    suppliers = pd.read_csv('./data/suppliers.csv')
    matched_supplier = suppliers[
        (suppliers["product"].str.strip().str.lower() == product.strip().lower()) &
        (suppliers["country"].str.strip().str.lower() == country.strip().lower())
    ]
    if matched_supplier.empty:
        return jsonify({"impact": None, "error": "Product/Country not found"}), 404

    cost = matched_supplier["cost"].values[0]
    new_cost = cost + (cost * new_tariff / 100)

    return jsonify({"product": product, "country": country, "impact": new_cost})


@app.route('/add_supplier', methods=['POST'])
def add_supplier():
    """Add new supplier"""
    data = request.json
    suppliers = pd.read_csv('./data/suppliers.csv')
    # global suppliers
    suppliers = pd.concat([suppliers, pd.DataFrame([data])], ignore_index=True)
    suppliers.to_csv('./data/suppliers.csv', index=False)  # Save to file
    return jsonify({"status": "success", "added": data})


@app.route("/debug_products", methods=["GET"])
def debug_products():
    suppliers = pd.read_csv('./data/suppliers.csv')
    """ Returns all available products in suppliers.csv """
    return jsonify(suppliers["product"].tolist())


@app.route("/top_suppliers", methods=["GET"])
def top_suppliers():
    """ Returns the top N suppliers for a given product based on cost """
    product = request.args.get('product')
    suppliers = pd.read_csv('./data/suppliers.csv')
    top_n = int(request.args.get('n', 3))
    matched = suppliers[suppliers["product"].str.lower().str.strip() == product.lower().strip()]
    if matched.empty:
        return jsonify({"error": "Product not found"}), 404
    top_matches = matched.sort_values(by="cost").head(top_n).to_dict(orient="records")
    return jsonify(top_matches)


@app.route("/cost_optimization", methods=["GET"])
def cost_optimization():
    """ Returns the supplier with the lowest cost for a given product """
    product = request.args.get('product')
    suppliers = pd.read_csv('./data/suppliers.csv')
    matched = suppliers[suppliers["product"].str.lower().str.strip() == product.lower().strip()]
    if matched.empty:
        return jsonify({"error": "Product not found"}), 404
    best_match = matched.sort_values(by="cost").iloc[0]
    return jsonify({
        "product": best_match["product"],
        "country": best_match["country"],
        "supplier": best_match["name"],
        "cost": best_match["cost"]
    })


# Do NOT run app.run() when deploying
if __name__ == '__main__':
    app.run(debug=True)

