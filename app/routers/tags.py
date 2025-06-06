from fastapi import APIRouter, Depends

from app.models import GetPostResult, TagInfo
from app.schema import Tag
from app.utils import Response
from app.utils.auth import get_current_user

router = APIRouter(prefix="/tags")


@router.get("/")
async def get_tags() -> Response[list[TagInfo]]:
    tags = await Tag.all()
    return Response.success(data=[tag.to_safe_dict() for tag in tags])


@router.post("/")
async def create_tag(name: str, user=Depends(get_current_user)) -> Response[TagInfo]:
    """
    创建标签
    """
    tag = await Tag.create(name=name)
    return Response.success(data=tag.to_safe_dict())


@router.delete("/{tag_id}")
async def delete_tag(tag_id: int, user=Depends(get_current_user)) -> Response:
    """
    删除标签
    """
    tag = await Tag.get_or_none(id=tag_id)
    if not tag:
        return Response.error(message="Tag not found")
    await tag.delete()
    return Response.success(message="Tag deleted")


@router.get("/{tag_id}")
async def get_post_by_tag(
    tag_id: int, page: int = 1, per_page: int = 10
) -> Response[GetPostResult]:
    """
    获取指定标签下的所有文章（支持分页）
    """
    tag = await Tag.get_or_none(id=tag_id)
    if not tag:
        return Response.error(message="Tag not found")

    # 预加载 posts 关系，避免 N+1 查询
    await tag.fetch_related("posts")

    # 获取分页数据
    offset = (page - 1) * per_page
    await tag.fetch_related("posts")
    posts = await tag.posts.offset(offset).limit(per_page)  # type: ignore
    # 计算总文章数
    total = len(await tag.posts)  # type: ignore

    # 返回 Result
    return Response.success(
        GetPostResult(
            page=page,
            per_page=per_page,
            posts=[await post.to_safe_dict() for post in posts],
            total=total,
        )
    )
