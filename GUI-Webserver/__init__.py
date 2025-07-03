# import os

# from flask import Flask, render_template, request, jsonify, send_file
# import csv 

# # write data to csv
# def append_to_csv(data):
#     file_name = "gui-webserver/static/csv/hmi_data.csv"
#     file_exists = False
#     labels = [
#         "FC501.AI.Value",
#         "FC501_OUT.Value",
#         "FC502.AI.Value",
#         "FC502_OUT.Value",
#         "LIT501.AI.Value",
#         "PT501.AI.Value",
#         "PT502.AI.Value",
#         "PT503.AI.Value",
#         "PT504.AI.Value",
#         'Purity Meter_DB."Purity Downstream"',
#         'Purity Meter_DB."Purity Upstream"',
#         "AIT501.AI.Value",
#         "TI501.AI.Value",
#         "TI502.AI.Value",
#         "TI503.AI.Value",
#         "TI504.AI.Value",
#         "TI505.AI.Value",
#         "TI523.AI.Value"
#     ]
#     print(data)
#     # Check if the file already exists
#     try:
#         with open(file_name, 'r'):
#             file_exists = True
#     except FileNotFoundError:
#         pass

#     # Append data to CSV
#     with open(file_name, 'a', newline='') as csvfile:
#         writer = csv.writer(csvfile)
#         if not file_exists:
#             writer.writerow(labels)  # Write header if file doesn't exist
#         writer.writerow(data)

# # create flask app
# def create_app(test_config=None):
#     # create and configure the app
#     app = Flask(__name__, instance_relative_config=True)
#     app.config.from_mapping(
#         SECRET_KEY='dev',
#         DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
#     )

#     if test_config is None:
#         # load the instance config, if it exists, when not testing
#         app.config.from_pyfile('config.py', silent=True)
#     else:
#         # load the test config if passed in
#         app.config.from_mapping(test_config)

#     # ensure the instance folder exists
#     try:
#         os.makedirs(app.instance_path)
#     except OSError:
#         pass
    
#     # attach db to app or something
#     from . import db
#     db.init_app(app)

#     @app.route('/')
#     def home():
#         return render_template('index.html')

#     @app.route('/data', methods=['GET', 'POST'])
#     def receive_data():
#         if request.method == 'GET':
#             return "Get out."
#         else:
#             data = request.get_json()
#             database = db.get_db()

#             # add data to database
#             try:
#                 database.execute(
#                     "INSERT INTO hmi (fc501_ai, fc501_out, fc502_ai, fc502_out, lit501_ai, pt501_ai, pt502_ai, pt503_ai, pt504_ai, purity_downstream, purity_upstream, ait501_ai, ti501_ai, ti502_ai, ti503_ai, ti504_ai, ti505_ai, ti523_ai) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
#                     data[:18],
#                 )
#                 database.commit()
#             except Exception as e:
#                 print(e)
#                 pass

#             return jsonify({'message': 'Data received', 'data': data}), 201

#     @app.route('/query_db', methods=['GET'])
#     def query_db():
#         try:
#             keys_param = request.args.get('keys')
#             start_time = request.args.get('start_time')  # e.g., '2025-05-19 00:00:00'
#             end_time = request.args.get('end_time')      # e.g., '2025-05-19 23:59:59'

#             if not keys_param:
#                 return jsonify({'error': 'No keys provided'}), 400

#             keys = keys_param.split(',')
#             columns = ', '.join(keys)

#             query = f"SELECT {columns}, created FROM hmi"
#             conditions = []
#             params = []

#             if start_time:
#                 conditions.append("created >= ?")
#                 params.append(start_time)
#             if end_time:
#                 conditions.append("created <= ?")
#                 params.append(end_time)

#             if conditions:
#                 query += " WHERE " + " AND ".join(conditions)

#             query += " ORDER BY created ASC"

#             database = db.get_db()
#             cursor = database.execute(query, params)
#             rows = cursor.fetchall()

#             data = [dict(row) for row in rows]

#             return jsonify({
#                 'columns': keys + ['created'],
#                 'data': data
#             })

#         except Exception as e:
#             print("Error in /query_db:", e)
#             return jsonify({'error': 'Server error'}), 500

#     return app