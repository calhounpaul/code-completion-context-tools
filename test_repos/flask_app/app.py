#!/usr/bin/env python3
"""Simple Flask application for testing."""

from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    """User model."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    posts = db.relationship('Post', backref='author', lazy=True)
    
    def to_dict(self):
        """Convert user to dictionary."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Post(db.Model):
    """Post model."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def to_dict(self):
        """Convert post to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'user_id': self.user_id
        }

@app.route('/')
def index():
    """Home page."""
    return jsonify({'message': 'Welcome to Flask API', 'status': 'running'})

@app.route('/users', methods=['GET', 'POST'])
def users():
    """Handle user operations."""
    if request.method == 'POST':
        data = request.get_json()
        if not data or 'username' not in data or 'email' not in data:
            return jsonify({'error': 'Missing required fields'}), 400
        
        try:
            user = User(username=data['username'], email=data['email'])
            db.session.add(user)
            db.session.commit()
            return jsonify(user.to_dict()), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    # GET request
    all_users = User.query.all()
    return jsonify([user.to_dict() for user in all_users])

@app.route('/users/<int:user_id>')
def get_user(user_id):
    """Get a specific user."""
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

@app.route('/posts', methods=['GET', 'POST'])
def posts():
    """Handle post operations."""
    if request.method == 'POST':
        data = request.get_json()
        required_fields = ['title', 'content', 'user_id']
        
        if not data or not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        try:
            post = Post(
                title=data['title'],
                content=data['content'],
                user_id=data['user_id']
            )
            db.session.add(post)
            db.session.commit()
            return jsonify(post.to_dict()), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    # GET request
    all_posts = Post.query.all()
    return jsonify([post.to_dict() for post in all_posts])

@app.route('/users/<int:user_id>/posts')
def user_posts(user_id):
    """Get all posts by a user."""
    user = User.query.get_or_404(user_id)
    posts = Post.query.filter_by(user_id=user_id).all()
    return jsonify({
        'user': user.to_dict(),
        'posts': [post.to_dict() for post in posts]
    })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)