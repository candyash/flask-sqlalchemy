import unittest
from flask.ext.testing import TestCase 
from app import create_app, db
from app.models import User, Friend
u1 = User(name='admin2', email='admin2@gmail.com', age=25)
u2 = User(name='test2', email='test2@gmail.com', age=27)

def _init_database():
    db.session.add_all([u1,u2])
    db.session.commit()
    return u1, u2

class BaseTestCase(TestCase):
    
    def create_app(self):
        self.app = create_app('testing')
        return self.app
    def setUp(self):
        
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        _init_database()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()


class  FastTestCase(BaseTestCase):
    
    #Ensuer that the index work perfectly
    def test_index_page(self):
        response=self.client.get('/',content_type='html/text')
        self.assertEqual(response.status_code, 200)
    def test_add_monkey(self):
        data={}
        response=self.client.get('/addMonkey')
        self.assertEqual(response.status_code, 200)
        response=self.client.post('/addMonkey',data=data, content_type='html/text')
        self.assertTrue('This field is required' in  response.data)
    def test_add_money_correct(self):
        data=dict(name='admin', email='adminu@gmail.com', age=25)
        response=self.client.get('/addMonkey')
        self.assertEqual(response.status_code, 200)
        response=self.client.post('/addMonkey',data=data,follow_redirects=True )
        self.assertTrue('User admin was registered successfully', response.data)
       
    def test_monkey_list(self):
        m1 = User(name='admin2', email='admin2@gmail.com', age=25)
        m2 = User(name='test2', email='test2@gmail.com', age=27)
        f=Friend(m2.id, approved=True, bestfriend=False)
        db.session.add(f)
        db.session.commit()
        m1.tag.append(f)
        db.session.commit()
        response=self.client.get('/',follow_redirects=True)
        self.assertIn('admin', response.data)
        response=self.client.get('/friends?id=1',follow_redirects=True)
        self.assertIn('Welcome! admin', response.data)
       
    def test_monkey_edit(self):
        response=self.client.get('/profile?id=1',follow_redirects=True )
        self.assertIn('Edit Profile', response.data)
        data=dict(name='admin', email='adminu@gmail.com', age=28)
        response=self.client.post('/profile?id=1',data=data,follow_redirects=True )
        self.assertTrue('You have been updated your profile' , response.data)
        
    def test_monkey_friend(self):
        response=self.client.get('/monkeyfriend?id=1')
        self.assertIn('Friend Monkeys! Enjoy!', response.data)
    def test_sort_by_name(self):
        m1 = User(name='admin2', email='admin2@gmail.com', age=25)
        m2 = User(name='test2', email='test2@gmail.com', age=27)
        db.session.add_all([m1, m2])
        db.session.commit()
        response=self.client.get('/sortbyname', follow_redirects=True )
        self.assertIn('Sort by name',  response.data)
    def test_sort_by_bfriend(self):
        a1 = User(name='admin3', email='admin3@gmail.com', age=25)
        a2 = User(name='test3', email='test3@gmail.com', age=27)
        f=Friend(friend_account=a2.id, approved=True, bestfriend=True)
        db.session.add_all([a1,a2])
        db.session.add(f)
        db.session.commit()
        a1.tag.append(f)
        db.session.commit()
        db.session.commit()
        response=self.client.get('/sortbybestfriend', follow_redirects=True )
        self.assertIn('Sort by Best friends',  response.data)
    def test_sort_by_nfriends(self):
        b1 = User(name='admin4', email='admin4@gmail.com', age=25)
        b2 = User(name='test4', email='test4@gmail.com', age=27)
        f=Friend(friend_account=b2.id, approved=True, bestfriend=False)
        db.session.add_all([a1,a2])
        db.session.add(f)
        db.session.commit()
        b1.tag.append(f)
        db.session.commit()
        response=self.client.get('/sortbynfriends', follow_redirects=True )
        self.assertIn('Sort by number of friends',  response.data)
   

         
        
    
      


