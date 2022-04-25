import flask
from flask import jsonify, request
from . import db_session
from .users import User
from .chats import Chats

blueprint = flask.Blueprint(
    'users_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/users')
def get_users():
    db_sess = db_session.create_session()
    users = db_sess.query(User).all()
    return jsonify(
        {
            'users':
                [item.to_dict(
                    only=('id', 'email', 'nickname', 'surname', 'name', 'group', 'modified_date'))
                    for item in users]
        }
    )


@blueprint.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    db_sess = db_session.create_session()
    users = db_sess.query(User).get(user_id)
    if not users:
        return jsonify({'error': 'Not found'})
    return jsonify(
        {
            'users': users.to_dict(only=('id', 'email', 'nickname', 'surname', 'name', 'group', 'modified_date'))
        }
    )


@blueprint.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_users(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)
    if not user:
        return jsonify({'error': 'Not found'})
    db_sess.delete(user)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/users', methods=['POST'])
def create_users():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['id', 'email', 'nickname', 'surname', 'name', 'group', 'hashed_password']):
        return jsonify({'error': 'Wrong params'})
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(request.json['id'])
    if user:
        return jsonify({'error': ' Id already exists'})
    users = User(
        id=request.json['id'],
        email=request.json['email'],
        nickname=request.json['nickname'],
        surname=request.json['surname'],
        name=request.json['name'],
        group="/".join(request.json['group'].split("/")[-4:]),
        hashed_password=request.json['hashed_password']
    )
    db_sess.add(users)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/users/<int:user_id>', methods=['PUT'])
def edit_users(user_id):
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['email', 'nickname', 'surname', 'name', 'group']):
        return jsonify({'error': 'Wrong params'})
    db_sess = db_session.create_session()
    users = db_sess.query(User).get(user_id)
    if not users:
        return jsonify({'error': 'Not found'})
    users.email = request.json['email']
    users.nickname = request.json['nickname']
    users.surname = request.json['surname']
    users.name = request.json['name']
    users.group = "/".join(request.json['group'].split("/")[-4:])
    db_sess.commit()
    return jsonify({'success': 'OK'})
