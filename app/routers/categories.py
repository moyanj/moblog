from fastapi import APIRouter, Depends

from app.models import CategoryInfo, GetPostResult
from app.schema import Category
from app.utils import Response
from app.utils.auth import get_current_user

router = APIRouter(prefix="/categories")


@router.get("/")
async def get_categories() -> Response[list[CategoryInfo]]:
    categories = await Category.all()
    return Response.success([category.to_safe_dict() for category in categories])


@router.post("/")
async def create_category(
    name: str, user=Depends(get_current_user)
) -> Response[CategoryInfo]:
    """
    创建标签
    """
    category = await Category.create(name=name)
    return Response.success(category.to_safe_dict())


@router.delete("/{category_id}")
async def delete_category(category_id: int, user=Depends(get_current_user)) -> Response:
    """
    删除标签
    """
    category = await Category.get_or_none(id=category_id)
    if not category:
        return Response.error(message="Category not found")
    await category.delete()
    return Response.success(message="Category deleted")


@router.get("/{category_id}")
async def get_post_by_category(
    category_id: int, page: int = 1, per_page: int = 10
) -> Response[GetPostResult]:
    """
    获取指定标签下的所有文章（支持分页）
    """
    category = await Category.get_or_none(id=category_id)
    if not category:
        return Response.error(message="Category not found")

    # 预加载 posts 关系，避免 N+1 查询
    await category.fetch_related("posts")

    # 获取分页数据
    offset = (page - 1) * per_page
    posts = await category.posts.offset(offset).limit(per_page)  # type: ignore
    # 计算总文章数
    total = len(category.posts)  # type: ignore

    # 返回 Result
    return Response.success(
        GetPostResult(
            page=page,
            per_page=per_page,
            posts=[await post.to_safe_dict() for post in posts],
            total=total,
        )
    )
