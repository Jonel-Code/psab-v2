from flask_restful import Resource, reqparse
from core.dummy_fetch_student_info import get_curriculum


def generate_student_curriculum_edges_and_node(course: str, year: str):
    json_curr = get_curriculum()[course.upper()][year]
    edges_list = []
    nodes = []
    for item in json_curr['subjects']:
        parent = item['code']
        childs = str(item['pre_req']).split(',')
        if len(childs) > 0:
            for c in childs:
                edges_list.append({'parent': parent, 'child': c})
        else:
            edges_list.append({'parent': parent, 'child': childs})
        new_node = ({'title': parent, 'label': item['title']})
        if new_node not in nodes:
            nodes.append(new_node)
    return edges_list, nodes


class CurriculumTree(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('course', help='course is required', required=True)
        parser.add_argument('curriculum_year', help='curriculum year is required', required=True)
        data = parser.parse_args()

        edges, nodes = generate_student_curriculum_edges_and_node(
            data['course'], data['curriculum_year'])
        return_value = {'edges': edges, 'nodes': nodes}

        return return_value if len(return_value) > 0 else {
            'message': 'no data found'}, 200 if len(return_value) > 0 is not None else 404, {
                   'Access-Control-Allow-Origin': '*'}
