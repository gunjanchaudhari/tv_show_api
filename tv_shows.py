
from doctest import Example
from flask import Flask
from flask_restx import Resource, abort, marshal, Api, Namespace, fields, reqparse
from flask import request
from utils.enums import Status
from utils import crud_utils as util
app = Flask(__name__)
api = Api(app)


class DictItem(fields.Raw):
    def output(self, key, obj, *args, **kwargs):
        try:
            dct = getattr(obj, self.attribute)
        except AttributeError:
            return {}
        return dct or {}


import_model = api.model('import_show', {
    'id': fields.String,
    'last-update': fields.String,
})

patch_model = api.model('patch_show', {

    "url": fields.String(
        description="Url of the show",
        example="https://www.tvmaze.com/shows/23542/good-girls"),
    "name": fields.String(
        description="Name of the show",
        example="Good Girls"),
    "language": fields.String(
        description="Language of the show",
        example="English"),
    "type": fields.String(example="Scripted"),
    "genres": fields.List(fields.String,
                          description="List of Genres",
                          example=[
                              "Drama",
                              "Comedy",
                              "Crime"]),
    "status": fields.String(
        description="Currently running or ended",
        example="Ended"),
    "runtime": fields.String(
        description="Duration of the show",
        example="60"),
    "premiered": fields.DateTime(
        required=True,
        description="premiered on date",
        example="2021-10-27"),
    "schedule": DictItem(example={
        "time": "21:00",
        "days": [
            "Thursday"
        ]
    }),
    "rating": DictItem(
        description="Rating on 10",
        example={
            "average": 7.2
        }),
    "network": DictItem(example={
        "id": 1,
        "name": "NBC",
        "country": {
            "name": "United States",
            "code": "US",
            "timezone": "America/New_York"
        },
        "officialSite": "https://www.nbc.com/"
    }),
    "weight": fields.String(example="95"),
})


@api.route('/tv_shows/import')
class Shows(Resource):

    """args is a dictionary containing the query params in the url.
        After the name is retrieved it is pass to import_show to insert the show"""
    # @api.marshal_list_with(import_model)
    @api.response(200, "Successfully imported TV show")
    @api.doc(params={"name": "Enter show name to be imported"})
    def post(self):
        """Import an existing show """

        name = request.args.get("name")
        #name = args['name']
        show_inf = util.import_show(name)
        if show_inf == Status.FAIL:
            return abort(500, "Show could not be imported")
        return show_inf


@api.route('/tv_shows/<int:id>')
class Show(Resource):
    @api.response(200, "Successfully imported TV show")
    def get(self, id):
        """Retrieve a show with id"""
        ret_show = util.get_show(id)
        print(type(ret_show))
        if ret_show == Status.FAIL:
            return abort(500, "Show could not be imported")
        print(type(ret_show))
        return ret_show

    @api.response(200, "Successfully deleted show")
    def delete(self, id):
        """Delete an existing show row"""
        status = util.del_show(id)
        if status == Status.SUCCESS:
            return {"message": "The tv show with id {} was removed from the database!".format(id), "id": id}, 200
        elif status == Status.NOT_EXIST:
            return {"message": "tv show id does not exist in the database"}
        elif status == Status.INVALID:
            return {"message": "No tv shows available to delete"}
        return abort(500, "Show could not be deleted")

    @api.expect(patch_model)
    @api.response(200, "Successfully deleted show")
    def patch(self, id):
        """Patch the show with the payload provided"""

        data = request.json
        show = util.change_fields(data, id)
        if show:
            return {"message": "the show has been patched {}".format(show)}
        return abort(500, "Show could not be patched")


if __name__ == '__main__':

    # run the application
    app.run(debug=True)
