from calendar import c
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException

from app.models import PostCreateModel, PostUpdateModel, PostInfo, GetPostResult
from app.schema import Category, Post, Tag, User
from app.utils import Response
from app.utils.auth import get_current_user

router = APIRouter(prefix="/posts")


@router.get("/")
async def get_posts(page: int = 1, per_page: int = 10) -> Response[GetPostResult]:
    """
    获取文章列表（支持分页）
    """
    offset = (page - 1) * per_page
    posts = await Post.all().offset(offset).limit(per_page)
    post_count = await Post.all().count()
    out = []
    for post in posts:
        await post.fetch_related("tags", "category", "author")
        out.append(post.to_safe_dict())
    return Response.success(
        GetPostResult(posts=out, total=post_count, page=page, per_page=per_page)
    )


@router.get("/{post_id}")
async def get_post_by_id(post_id: int) -> Response[PostInfo]:
    """
    根据文章 ID 获取文章详情
    """
    post = await Post.get_or_none(id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    await post.fetch_related("tags", "category", "author")
    return Response(data=post.to_safe_dict())


@router.post("")
async def create_post(
    data: PostCreateModel, user: User = Depends(get_current_user)
) -> Response[dict[str, int]]:
    """
    创建新文章
    """

    category = await Category.get_or_none(id=data.category_id)
    if category is None:
        return Response.error("Category not found", 404)
    tags = []
    for tag_name in data.tag_names:
        tag = await Tag.get_or_none(name=tag_name)
        if tag is None:
            return Response(
                data={"tag": tag}, message="Tag not found", status_code=404
            ).ret()
        tags.append(tag)

    post = await Post.create(
        title=data.title,
        summary=data.summary,
        content=data.content,
        author=user,
        tags=tags,
        category=category,
    )
    return Response(data={"id": post.id}, message="Post created")


@router.put("/{post_id}")
async def update_post(
    post_id: int, data: PostUpdateModel, user: User = Depends(get_current_user)
) -> Response:
    """
    更新文章信息
    """
    post = await Post.get_or_none(id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    post.update_from_dict(data.model_dump(exclude_unset=True))
    await post.save()
    return Response(message="Post updated")


@router.delete("/{post_id}")
async def delete_post(post_id: int, user: User = Depends(get_current_user)) -> Response:
    """
    删除文章
    """
    post = await Post.get_or_none(id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    await post.delete()
    return Response(message="文章删除成功")
