
from flask import Flask
from flask_restx import Resource, abort, marshal, Api, Namespace, fields, reqparse
from flask import request
from utils.enums import Status
from utils import crud_utils as util

app = Flask(__name__)
api = Api(app)


import_model = api.model('import_show', {
    'id': fields.String,
    'last-update': fields.String,
    '_links': {'self': {'href': fields.String}}
})


@api.route('/tv_shows/import')
class Shows(Resource):

    """args is a dictionary containing the query params in the url. 
        After the name is retrieved it is pass to import_show to insert the show"""
    # @api.marshal_list_with(import_model)
    @api.response(200, "Successfully imported TV show")
    @api.doc(params={"name": "Enter show name to be imported"})
    def post(self):

        name = request.args.get("name")
        #name = args['name']
        show_inf = util.import_show(name)
        if show_inf == Status.FAIL:
            return abort(500, "Show could not be imported")
        return show_inf


if __name__ == '__main__':

    # run the application
    app.run(debug=True)
