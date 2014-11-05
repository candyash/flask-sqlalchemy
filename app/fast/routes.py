from flask import render_template, flash, redirect, \
    url_for, abort, request, current_app
from ..import db
from ..models import User, Friend
from . import fast
from .forms import AddMonkeyForm
from config import Config
from flask.ext.sqlalchemy import Pagination
from sqlalchemy import func


@fast.route("/", defaults={"page": 1})
@fast.route("/")
def index():
    pagination = []
    user_list = []
    """To list all users"""
    page = request.args.get("page", 1, type=int)
    pagination = User.query.order_by(User.member_since.desc()).\
        paginate(page,
                 per_page=current_app.config["USER_PER_PAGE"], error_out=False)
    user_list = pagination.items
    return render_template("fast/index.html",
                           pagination=pagination, user=user_list)


@fast.route("/addMonkey", methods=["GET", "POST"])
def addMonkey():
    """add a new monkey."""
    form = AddMonkeyForm()
    try:
        if request.method == "POST" and form.validate_on_submit():
            name = form.Name.data
            email = form.Email.data
            age = form.Age.data
            user = User(name=name, email=email, age=age)
            db.session.add(user)
            db.session.commit()
            flash("User {0} was registered successfully.".format(name))
            return redirect(url_for("fast.index"))
    except:
        flash("Error is found. The user already registerd to the system!")
    return render_template("fast/addmonkey.html", form=form)


@fast.route("/monkey", methods=["GET", "POST"])
def monkeyProfile():
    """initializing presonalinfo for the current user"""
    id_monkey = request.args.get("id", type=int)
    user = User.query.get(id_monkey)
    return render_template('fast/user.html', user=user)


@fast.route('/profile', methods=['GET', 'POST'])
def edit():
    form = AddMonkeyForm()
    id_monkey = request.args.get("id", type=int)
    user = User.query.filter(User.id == id_monkey).first()
    if form.validate_on_submit():
        user.name = form.Name.data
        user.email = form.Email.data
        user.age = form.Age.data
        user.id = id_monkey
        db.session.add(user)
        db.session.commit()
        flash("You have been updated your profile")
        return redirect(url_for('fast.index'))
    if user:
        form.Name.data = user.name
        form.Email.data = user.email
        form.Age.data = user.age
    return render_template('fast/profile.html', form=form)


@fast.route("/monkeyfriend", defaults={"page": 1})
@fast.route("/monkeyfriend", methods=['GET', 'POST'])
def monkeyfriend():
    id_monkey = request.args.get("id", type=int)
    btn_best = False
    pagination = []
    user_list = []
    f_account = []
    m_user = User.query.filter(User.id == id_monkey).first()
    q = Friend.query.join(User.tag).filter(User.id == id_monkey).filter(Friend.bestfriend == True ).first()
    if q is None:
        btn_best = True
    elif q.bestfriend:
        btn_best = False
    """Friend add check"""
    check = Friend.query.join(User.tag).filter(User.id == id_monkey)
    if check:
        for i in check:
            f_account.append(i.friend_account)
    """To list all users"""
    page = request.args.get("page", 1, type=int)
    pagination = User.query.filter(User.id != id_monkey).filter(User.id.notin_(f_account)).\
        order_by(User.member_since.desc()).\
        paginate(page, per_page=current_app.config["USER_PER_PAGE"],
                 error_out=False)
    user_list = pagination.items
    if len(user_list) == 0:
        flash("Thank you! you add all monkeys as friend.")
    return render_template("fast/monkeyfriends.html", pagination=pagination,
                           btn_best=btn_best, user=user_list,
                           id_monkey=id_monkey, m_user=m_user)


@fast.route("/confirm", methods=["GET", "PUT"])
def confirm():
    """getting the id of both monkey"""
    id_friend = request.args.get("id", type=int)
    id_user = request.args.get("id2", type=int)
    """friend confirmation"""
    mainMonkey = User.query.get(id_user)
    othermonkey = User.query.get(id_friend)
    q = Friend.query.join(User.tag).filter(Friend.friend_account == id_friend).\
        filter(User.id == id_user).first()
    if q is None:
        f = Friend(friend_account=id_friend, approved=True, bestfriend=False)
        db.session.add(f)
        db.session.commit()
        tag = mainMonkey.tag.append(f)
        db.session.commit()
        flash("Thank you! Now,{0} is your Friend!!".format(othermonkey.name))
        return redirect(url_for("fast.index"))
    else:
            flash("Remember you sent friend request!")
    return redirect(url_for("fast.index"))


@fast.route("/delete/<int:id>", methods=["GET", "DELETE"])
def delete(id):
    """remove monkey"""
    user = User.query.get_or_404(id)
    try:
        if user:
            db.session.delete(user)
            db.session.commit()
            flash("{0} is removed!".format(user.name))
            return redirect(url_for("fast.index"))
    except:
        flash("database missing \n")
    return redirect(url_for("fast.index"))


@fast.route("/friends", defaults={"page": 1})
@fast.route("/friends", methods=["GET", "POST"])
def friends():
    f_account = []
    """To list all friends"""
    id_user = request.args.get('id', type=int)
    m_user = User.query.filter(User.id == id_user).first()
    page = request.args.get("page", 1, type=int)
    """Friend add check"""
    check = Friend.query.join(User.tag).filter(User.id == id_user)
    if check:
        for i in check:
            f_account.append(i.friend_account)
    pag = User.query.filter(User.id != id_user).filter(User.id.in_(f_account)).\
        order_by(User.member_since.desc()).\
        paginate(page, per_page=current_app.config["USER_PER_PAGE"],
                 error_out=False)
    user_l = pag.items
    if len(user_l) == 0:
        flash("Please Friend monkeys!")
    return render_template('fast/friends.html', pag=pag, user_l=user_l,
                           m_user=m_user, id_user=id_user)


@fast.route('/unFriend', methods=['GET', 'DELETE'])
def unfriend():
    """deleting friend from friendship list"""
    id_friend = request.args.get("id", type=int)
    id_user = request.args.get("id2", type=int)
    mainMonkey = User.query.get(id_user)
    f_Monkey = User.query.get(id_friend)
    othermonkey = Friend.query.filter(Friend.friend_account == id_friend).\
        first()
    f_all = mainMonkey.tag
    f_remove = f_all.remove(othermonkey)
    db.session.delete(othermonkey)
    db.session.commit()
    flash("you are unfreind {0}!! \n".format(f_Monkey.name))
    return redirect(url_for('fast.index'))


@fast.route('/bestFriend')
def bestFriend():
    """best friend list if there is best friend for the current user """
    """getting the id of both monkey"""
    id_friend = request.args.get("id", type=int)
    id_user = request.args.get("id2", type=int)
    """friend confirmation"""
    mainMonkey = User.query.get(id_user)
    othermonkey = User.query.get(id_friend)
    q = Friend.query.join(User.tag).filter(Friend.friend_account == id_friend).\
        filter(User.id == id_user).first()
    if q is None:
        f = Friend(friend_account=id_friend, approved=True, bestfriend=True)
        db.session.add(f)
        db.session.commit()
        tag = mainMonkey.tag.append(f)
        db.session.commit()
        flash("Thank you! Now, {0} is your best friend!!".
              format(othermonkey.name))
        return redirect(url_for("fast.index"))
        q.bestfriend = True
        db.session.add(q)
        db.session.commit()
        return redirect(url_for("fast.index"))
    elif not q.bestfriend:
        q.bestfriend = True
        db.session.add(q)
        db.session.commit()
        return redirect(url_for("fast.index"))
    else:
        flash("You have best friend!")
    return redirect(url_for("fast.index"))


@fast.route("/sortbyname", defaults={"page": 1})
@fast.route("/sortbyname")
def sortbyname():
    pagination = []
    user_list = []
    """To list all users"""
    check = True
    page = request.args.get("page", 1, type=int)
    pagination = User.query.order_by(User.name.asc()).\
        paginate(page,
                 per_page=current_app.config["USER_PER_PAGE"], error_out=False)
    user_list = pagination.items
    return render_template("fast/index.html",
                           pagination=pagination, user=user_list, check=check)


@fast.route("/sortbybestfriend", defaults={"page": 1})
@fast.route("/sortbybestfriend")
def sortbybfriend():
    check2 = True
    pagination = []
    user_list = []
    """To list all users"""
    page = request.args.get("page", 1, type=int)
    pagination = User.query.join(User.tag).filter(Friend.bestfriend==True).order_by(Friend.bestfriend.asc()).\
        paginate(page,
                 per_page=current_app.config["USER_PER_PAGE"], error_out=False)
    user_list = pagination.items
    return render_template("fast/index.html",
                           pagination=pagination, user=user_list, check2=check2)


@fast.route("/sortbynfriends", defaults={"page": 1})
@fast.route("/sortbynfriends")
def sortbynfriends():
    check3 = True
    pagination = []
    user_list = []
    """To list all users"""
    page = request.args.get("page", 1, type=int)
    pagination = User.query.join(User.tag).order_by(func.count(Friend.approved).desc()).group_by(User.id).\
        paginate(page,
                 per_page=current_app.config["USER_PER_PAGE"], error_out=False)
    user_list = pagination.items
    return render_template("fast/index.html",
                           pagination=pagination, user=user_list, check3=check3)
