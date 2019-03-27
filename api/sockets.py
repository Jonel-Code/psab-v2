def init_socket(debug=True):
    from deploy import app, socketio
    socketio.run(app, debug=debug)


def advising_socket_emit(name, response):
    from deploy import socketio
    socketio.emit(name,
                  response,
                  namespace='/advising')


class AdvisingConfigs:
    new_advising_form_submitted = 'new advising form submitted'
    new_opened_subject = 'new_opened_subject'

# def messageReceived(methods=['GET', 'POST']):
#     print('message was received!!!')
#
#
# @socketio.on('my event')
# def handle_my_custom_event(json, methods=['GET', 'POST']):
#     print('received my event: ' + str(json))
#     socketio.emit('my response', json, callback=messageReceived)
