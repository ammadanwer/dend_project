import base64
import io

from flask import Flask, request, render_template, Response
from matplotlib.backends.backend_template import FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from create_tables import connect_database
from sql_queries import GET_STATE_DATA, GET_COUNTY_DATA

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    cur, conn = connect_database()
    cur.execute("SELECT * FROM dim_county WHERE mod(fips_id, 1000)=0 AND state != 'US';")
    states = cur.fetchall()
    graph_data = []
    if request.method == 'GET':
        return render_template('index.html', states=states)
    else:
        print(request.form)
        granularity = request.form.get('granularity_select', '')
        if granularity == 'state':
            print(GET_STATE_DATA)
            cur.execute(GET_STATE_DATA)
            graph_data = cur.fetchall()
        elif granularity == 'county':
            state_code = request.form.get('state_select', '')
            sql = GET_COUNTY_DATA.format(state_code=state_code.lower())
            print(sql)
            cur.execute(sql)
            graph_data = cur.fetchall()
        if granularity in ['state', 'county']:
            x_list = []
            y_list = []
            txt_list = []
            for data in graph_data:
                x_list.append(data[4])
                y_list.append(data[3])
                txt_list.append(data[1])
            fig, ax = plt.subplots()
            for i, txt in enumerate(txt_list):
                ax.annotate(txt.replace(' County', ''), (x_list[i], y_list[i]))
            ax.scatter(x_list, y_list)
            plt.xlabel('Unemployment %')
            plt.ylabel('Poverty %')
            output = io.BytesIO()
            fig.savefig(output, format='png')
            output.seek(0)
            buffer = b''.join(output)
            b2 = base64.b64encode(buffer)
            image_src = b2.decode('utf-8')
            return render_template('index.html', states=states, image_src=image_src)
    return render_template('index.html', states=states)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
