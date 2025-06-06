from operator import index
from typing import Optional

from tortoise import fields
from tortoise.indexes import Index
from tortoise.models import Model

import app.models as models
from app.models.response import CategoryInfo, TagInfo


class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(
        max_length=255, unique=True, index=True, validators=[lambda x: x != "me"]
    )  # 用户名
    password = fields.CharField(max_length=60)  # 密码（sha256）
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    avatar = fields.CharField(max_length=255, null=True)
    is_admin = fields.BooleanField(default=False)

    def __str__(self):
        return f"User({self.username},{self.id})"

    def to_safe_dict(self):
        return models.UserInfo(
            username=self.username,
            avatar=self.avatar,
            created_at=self.created_at.isoformat(),
            is_admin=self.is_admin,
            updated_at=self.updated_at.isoformat(),
        )

    class Meta:  # type: ignore
        table = "users"
        indexes = [Index(fields=["username", "id"])]


class Tag(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255, unique=True, index=True)  # 标签名

    def __str__(self):
        return self.name

    def to_safe_dict(self):
        return TagInfo(
            id=self.id,
            name=self.name,
        )

    class Meta:  # type: ignore
        table = "tags"


class Category(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255, unique=True, index=True)  # 类别名

    def __str__(self):
        return self.name

    def to_safe_dict(self):
        return CategoryInfo(
            id=self.id,
            name=self.name,
        )

    class Meta:  # type: ignore
        table = "categories"


class Post(Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=255)  # 标题
    summary = fields.TextField()  # 摘要
    content = fields.TextField()  # 内容（Markdown）
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    author = fields.ForeignKeyField("models.User", related_name="posts")  # 作者
    tags = fields.ManyToManyField("models.Tag", related_name="posts")  # 标签
    category = fields.ForeignKeyField("models.Category", related_name="posts")
    comments = fields.ReverseRelation["Comment"]

    def __str__(self):
        return f"Post({self.title},{self.id})"

    async def to_safe_dict(self):
        await self.fetch_related("tags")
        return models.PostInfo(
            id=self.id,
            title=self.title,
            summary=self.summary,
            tags=[tag.name for tag in self.tags],
            content=self.content,
            author=(await self.author.first()).username,
            category=(await self.category.first()).name,
            created_at=self.created_at.isoformat(),
            updated_at=self.updated_at.isoformat(),
        )

    class Meta:  # type: ignore
        table = "posts"


class Comment(Model):
    id = fields.IntField(pk=True)
    content = fields.TextField()  # 内容
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    author = fields.ForeignKeyField("models.User", related_name="comments")  # 作者
    post = fields.ForeignKeyField("models.Post", related_name="comments")

    def __str__(self):
        return f"Comment({self.content[:50]},{self.id})"

    class Meta:  # type: ignore
        table = "comments"


class Config(Model):
    id = fields.IntField(pk=True)
    key = fields.CharField(max_length=255, unique=True, index=True)  # 配置键
    value = fields.TextField()  # 配置值

    def __str__(self):
        return f"Config({self.key},{self.value})"

    @classmethod
    async def init(cls):
        if await cls.get_val("init", "n") == "n":
            print("初始化数据库...")
            for key, value in {
                "site_title": "My Blog",
                "site_description": "A blog built with Tortoise ORM",
                "site_keywords": "tortoise,orm,blog",
                "site_logo": "",
                "init": "y",
            }.items():
                await cls.set_val(key, value)

    @classmethod
    async def get_val(cls, key: str, default: Optional[str] = None):
        c = await cls.get_or_none(key=key)
        if c is None:
            return default
        return c.value

    @classmethod
    async def set_val(cls, key: str, value: str):
        c = await cls.get_or_create(key=key, defaults={"value": value})
        c[0].value = value
        await c[0].save()

    class Meta:  # type: ignore
        table = "configs"


class Page(Model):
    id = fields.IntField(pk=True, index=True)
    slug = fields.CharField(max_length=255, unique=True)
    content = fields.TextField()
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    def __str__(self):
        return f"Page({self.slug})"

    class Meta:  # type: ignore
        table = "pages"


class Resource(Model):
    id = fields.CharField(max_length=32, pk=True, index=True)  # xxh3_128
    path = fields.CharField(max_length=255)  # 资源路径
    desc = fields.CharField(max_length=255)  # 描述
    created_at = fields.DatetimeField(auto_now_add=True)  #  创建时间

    def __str__(self):
        return f"Resource({self.id})"
