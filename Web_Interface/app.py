from flask import Flask, render_template, request, jsonify
import pickle
import numpy as np
import os

categories=['Books', 'Fashion', 'Sports', 'Beauty', 'Electronics','Home & Kitchen']
regions=['North America', 'Asia', 'Europe', 'Middle East']

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, 'templates'),
    static_folder=os.path.join(BASE_DIR, 'static')
)

# Load ML models
MODEL_PATH = 'models'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'models')

def load_model(filename):
    path = os.path.join(MODEL_PATH, filename)
    return pickle.load(open(path, 'rb'))

logistic_model = load_model('logistic_model.pkl')
linear_model = load_model('linear_model.pkl')

#dictionary implementation...

dict_keys=['price', 'discount_percent', 'quantity_sold', 'discounted_price',
       'total_revenue', 'High_Demand', 'product_category_Beauty',
       'product_category_Books', 'product_category_Electronics',
       'product_category_Fashion', 'product_category_Home & Kitchen',
       'product_category_Sports', 'customer_region_Asia',
       'customer_region_Europe', 'customer_region_Middle East',
       'customer_region_North America']
lin_dict_keys=['price', 'discount_percent', 'quantity_sold', 'discounted_price',
       'High_Demand', 'product_category_Beauty',
       'product_category_Books', 'product_category_Electronics',
       'product_category_Fashion', 'product_category_Home & Kitchen',
       'product_category_Sports', 'customer_region_Asia',
       'customer_region_Europe', 'customer_region_Middle East',
       'customer_region_North America']
log_dict_keys=['price', 'discount_percent', 'quantity_sold', 'discounted_price',
       'product_category_Beauty',
       'product_category_Books', 'product_category_Electronics',
       'product_category_Fashion', 'product_category_Home & Kitchen',
       'product_category_Sports', 'customer_region_Asia',
       'customer_region_Europe', 'customer_region_Middle East',
       'customer_region_North America']

data_log = {}
for key in log_dict_keys:
    data_log[key] = 0
data_lin = {}
for key in lin_dict_keys:
    data_lin[key] = 0

@app.route('/', methods=['GET', 'POST'])
def index():

    reg_res = None
    class_res = None

    if request.method == 'POST':

        data_log = dict.fromkeys(log_dict_keys, 0)
        data_lin = dict.fromkeys(lin_dict_keys, 0)

        price = float(request.form.get('price'))
        discount = float(request.form.get('discount'))
        sold_units = int(request.form.get('sold_units'))

        cat_input = request.form.get('category').strip()
        reg_input = request.form.get('region').strip()

        category = f'product_category_{cat_input}'
        region = f'customer_region_{reg_input}'

        discounted_price = price * (1 - discount/100)

        for d in [data_log, data_lin]:
            d['price'] = price
            d['discount_percent'] = discount
            d['quantity_sold'] = sold_units
            d['discounted_price'] = discounted_price

        data_lin['High_Demand'] = 0  # or real logic

        data_log[category] = 1
        data_log[region] = 1
        data_lin[category] = 1
        data_lin[region] = 1

        lin_input = np.array([[data_lin[key] for key in lin_dict_keys]])
        log_input = np.array([[data_log[key] for key in log_dict_keys]])

        reg_res = linear_model.predict(lin_input)[0]
        class_res = logistic_model.predict(log_input)[0]

    return render_template(
        'index.html',
        categ=categories,
        reg=regions,
        reg_res=reg_res,
        class_res=class_res
    )

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()

    # Reset dicts
    data_log = dict.fromkeys(log_dict_keys, 0)
    data_lin = dict.fromkeys(lin_dict_keys, 0)

    # Extract values
    price = float(data['price'])
    discount = float(data['discount'])
    sold_units = int(data['sold_units'])
    category_input = data['category']
    region_input = data['region']

    category = f'product_category_{category_input}'
    region = f'customer_region_{region_input}'

    discounted_price = price * (1 - discount / 100)

    for d in (data_log, data_lin):
        d['price'] = price
        d['discount_percent'] = discount
        d['quantity_sold'] = sold_units
        d['discounted_price'] = discounted_price

    data_lin['High_Demand'] = 0

    data_log[category] = 1
    data_log[region] = 1
    data_lin[category] = 1
    data_lin[region] = 1

    lin_input = np.array([[data_lin[k] for k in lin_dict_keys]])
    log_input = np.array([[data_log[k] for k in log_dict_keys]])

    sales_prediction = float(linear_model.predict(lin_input)[0])
    class_prediction = int(logistic_model.predict(log_input)[0])

    confidence = max(logistic_model.predict_proba(log_input)[0])

    return jsonify({
        "success": True,
        "prediction": class_prediction,
        "sales_prediction": round(sales_prediction, 2),
        "confidence": round(confidence, 2)
    })


if __name__ == '__main__':
    app.run(debug=True)
