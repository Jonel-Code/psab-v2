def quick_parse(args: list((str, bool))):
    from flask_restful import reqparse
    parser = reqparse.RequestParser()
    for x in args:
        name = x[0]
        h = f'{x[0]} is {"required" if x[1] else "optional"}'
        parser.add_argument(name, help=h, required=x[1])
    return parser
