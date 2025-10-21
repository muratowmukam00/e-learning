from app.schemas.user import (
    UserBase, UserCreate, UserUpdate,
    UserPasswordChange, UserResponse, UserShort, UserList
)
from app.schemas.auth import (
    LoginRequest, Token, RefreshTokenRequest,
    AuthResponse, TokenPayload
)

from app.schemas.course import (
    CourseCreate, CourseUpdate, CourseResponse,
    CourseList, CourseShort, CourseFilter, CoursePublish
)
from app.schemas.category import (
    CategoryCreate, CategoryUpdate, CategoryResponse, CategoryShort
)

from app.schemas.lessons import (
    LessonCreate, LessonUpdate, LessonResponse,LessonListResponse
)

from app.schemas.enrollment import (
    EnrollmentCreate, EnrollmentResponse, StudentListResponse,
    CheckEnrollmentResponse, EnrollmentStats, EnrollmentDetail,
    CourseInfo, EnrollmentWithCourse, StudentInfo
)

from app.schemas.review import (
    ReviewCreate, ReviewUpdate, ReviewResponse, CheckReviewResponse,
    ReviewStats, ReviewWithUser, CourseWithReviews
)

from app.schemas.progress import (
    ProgressCreate, ProgressUpdate, ProgressResponse,
    LessonProgressResponse, CourseProgressSummary, StudentStatistics
)

__all__ = [
    # User schemas
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserPasswordChange",
    "UserResponse",
    "UserShort",
    "UserList",
    "LoginRequest",
    # Auth schemas
    "Token",
    "RefreshTokenRequest",
    "AuthResponse",
    "TokenPayload",
    # Course schemas
    "CourseCreate",
    "CourseUpdate",
    "CourseResponse",
    "CourseList",
    "CourseShort",
    "CourseFilter",
    "CoursePublish",
    # Category schemas
    "CategoryCreate",
    "CategoryUpdate",
    "CategoryResponse",
    "CategoryShort",
    # Lesson schemas
    "LessonCreate",
    "LessonUpdate",
    "LessonResponse",
    "LessonListResponse",
    # Enrollment schemas
    "EnrollmentCreate",
    "EnrollmentResponse",
    "StudentListResponse",
    "CheckEnrollmentResponse",
    "EnrollmentStats",
    "EnrollmentDetail",
    "CourseInfo",
    "EnrollmentWithCourse",
    "StudentInfo"
    # Review schemas
    "ReviewCreate",
    "ReviewUpdate",
    "ReviewResponse",
    "CheckReviewResponse",
    "ReviewStats",
    "ReviewWithUser",
    "CourseWithReviews"
    # Progress schemas
    "ProgressCreate",
    "ProgressUpdate",
    "ProgressResponse",
    "LessonProgressResponse",
    "CourseProgressSummary",
    "StudentStatistics"
]