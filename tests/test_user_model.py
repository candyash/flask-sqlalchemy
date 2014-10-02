import unittest
from app import create_app, db
from app.models import User,PersonalInfo,Friend, BestFriend, load_user


class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        #db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_setter(self):
        u = User(password='dmz')
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        u = User(password='dmz')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        u = User(password='dmz')
        self.assertTrue(u.verify_password('dmz'))
        self.assertFalse(u.verify_password('kdm'))

    def test_password_salts_are_random(self):
        u = User(password='dmz')
        u2 = User(password='kmd')
        self.assertTrue(u.password_hash != u2.password_hash)

    def test_user_loader(self):
        db.create_all()
        u = User(email='ash@gmail.com', username='dmesh', password='dmz')
        db.session.add(u)
        db.session.commit()
        self.assertTrue(load_user(u.id) == u)

   
    def test_approval(self):
        db.create_all()
        u1 = User(email='ash@example.com', username='ash', password='123')
        u2 = User(email='selam@example.com', username='sel', password='124',is_admin=True)
        p1 = PersonalInfo(firstName='ashenafi', lastName='kebe', Age=21, Bio='p',users=ul)
        p2 = PersonalInfo(firstName='selam', lastName='leg', Age=20, Bio='B',users=u2)
        f1 = Friend(user_account=1, friend_Account=2, status=True, approved=True, friends=ul)
        f2 = Friend(user_account=2, friend_Account=1, status=False, approved=False, friends=u2)
        db.session.add_all([u1, u2, p1,p2, f1, f2])
        db.session.commit()
        app1 = u1.for_approval().all()
        app2 = u2.for_approval().all()
        self.assertTrue(len(app1) == 1)
        self.assertTrue(app1[0] == f1)
        self.assertTrue(len(app2) == 0)
    def test_status(self):
         db.create_all()
         u1 = User(email='ash@example.com', username='ash', password='ash')
         u2 = User(email='selam@example.com', username='selam', password='124')
         p1 = PersonalInfo(firstName='ash', lastName='kebe', Age=21, Bio='p',users=ul)
         p2 = PersonalInfo(firstName='selam', lastName='leg', Age=20, Bio='B',users=u2)
         f1 = Friend(user_account=1, friend_Account=2, status=True, approved=True, friends=tl)
         f2 = Friend(user_account=2, friend_Account=1, status=False, approved=False, friends=t2)
         db.session.add_all([u1, u2, p1,p2, f1, f2])
         db.session.commit()
         
         app1 = u1.friend_status.all()
         app2 = u2.friend_status.all()
     
         self.assertTrue(len(app1) == 1)
         self.assertTrue(app1[0] == f1)
         self.assertTrue(len(app2) == 0)
         
        
    
      


