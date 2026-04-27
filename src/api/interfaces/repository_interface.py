"""Repository interface definitions.

Defines abstract base classes and protocols for the data access layer,
ensuring consistent repository contracts across the application.
"""

from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar

T = TypeVar("T")


class RepositoryInterface(ABC, Generic[T]):
    """Abstract base class for all repositories.

    Defines the standard CRUD contract that all repository implementations
    must follow. Type parameter T represents the entity type.
    """

    @abstractmethod
    def find_by_id(self, entity_id: int) -> Optional[T]:
        """Retrieve an entity by its primary key.

        Args:
            entity_id: The unique identifier of the entity.

        Returns:
            The entity if found, None otherwise.
        """
        ...

    @abstractmethod
    def find_by_username(self, username: str) -> Optional[T]:
        """Retrieve an entity by its username.

        Args:
            username: The username to search for.

        Returns:
            The entity if found, None otherwise.
        """
        ...

    @abstractmethod
    def save(self, entity: T) -> T:
        """Persist a new entity to the data store.

        Args:
            entity: The entity instance to save.

        Returns:
            The saved entity with any generated fields populated.

        Raises:
            ValueError: If the entity data is invalid.
        """
        ...

    @abstractmethod
    def delete(self, entity_id: int) -> bool:
        """Remove an entity by its primary key.

        Args:
            entity_id: The unique identifier of the entity to delete.

        Returns:
            True if the entity was deleted, False if not found.
        """
        ...

    @abstractmethod
    def find_all(self, skip: int = 0, limit: int = 100) -> list[T]:
        """Retrieve a paginated list of all entities.

        Args:
            skip: Number of records to skip (for pagination).
            limit: Maximum number of records to return.

        Returns:
            A list of entities.
        """
        ...

    @abstractmethod
    def count(self) -> int:
        """Return the total number of entities.

        Returns:
            Total entity count.
        """
        ...

    @abstractmethod
    def exists(self, entity_id: int) -> bool:
        """Check if an entity exists by its primary key.

        Args:
            entity_id: The unique identifier to check.

        Returns:
            True if the entity exists, False otherwise.
        """
        ...
"""Repository interface definitions.

Defines abstract base classes and protocols for the data access layer,
ensuring consistent repository contracts across the application.
"""

from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar

T = TypeVar("T")


class RepositoryInterface(ABC, Generic[T]):
    """Abstract base class for all repositories.

    Defines the standard CRUD contract that all repository implementations
    must follow. Type parameter T represents the entity type.
    """

    @abstractmethod
    def find_by_id(self, entity_id: int) -> Optional[T]:
        """Retrieve an entity by its primary key.

        Args:
            entity_id: The unique identifier of the entity.

        Returns:
            The entity if found, None otherwise.
        """
        ...

    @abstractmethod
    def find_by_username(self, username: str) -> Optional[T]:
        """Retrieve an entity by its username.

        Args:
            username: The username to search for.

        Returns:
            The entity if found, None otherwise.
        """
        ...

    @abstractmethod
    def save(self, entity: T) -> T:
        """Persist a new entity to the data store.

        Args:
            entity: The entity instance to save.

        Returns:
            The saved entity with any generated fields populated.

        Raises:
            ValueError: If the entity data is invalid.
        """
        ...

    @abstractmethod
    def delete(self, entity_id: int) -> bool:
        """Remove an entity by its primary key.

        Args:
            entity_id: The unique identifier of the entity to delete.

        Returns:
            True if the entity was deleted, False if not found.
        """
        ...

    @abstractmethod
    def find_all(self, skip: int = 0, limit: int = 100) -> list[T]:
        """Retrieve a paginated list of all entities.

        Args:
            skip: Number of records to skip (for pagination).
            limit: Maximum number of records to return.

        Returns:
            A list of entities.
        """
        ...

    @abstractmethod
    def count(self) -> int:
        """Return the total number of entities.

        Returns:
            Total entity count.
        """
        ...

    @abstractmethod
    def exists(self, entity_id: int) -> bool:
        """Check if an entity exists by its primary key.

        Args:
            entity_id: The unique identifier to check.

        Returns:
            True if the entity exists, False otherwise.
        """
        ...
"""Repository interface definitions.

Defines abstract base classes and protocols for the data access layer,
ensuring consistent repository contracts across the application.
"""

from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar

T = TypeVar("T")


class RepositoryInterface(ABC, Generic[T]):
    """Abstract base class for all repositories.

    Defines the standard CRUD contract that all repository implementations
    must follow. Type parameter T represents the entity type.
    """

    @abstractmethod
    def find_by_id(self, entity_id: int) -> Optional[T]:
        """Retrieve an entity by its primary key.

        Args:
            entity_id: The unique identifier of the entity.

        Returns:
            The entity if found, None otherwise.
        """
        ...

    @abstractmethod
    def find_by_username(self, username: str) -> Optional[T]:
        """Retrieve an entity by its username.

        Args:
            username: The username to search for.

        Returns:
            The entity if found, None otherwise.
        """
        ...

    @abstractmethod
    def save(self, entity: T) -> T:
        """Persist a new entity to the data store.

        Args:
            entity: The entity instance to save.

        Returns:
            The saved entity with any generated fields populated.

        Raises:
            ValueError: If the entity data is invalid.
        """
        ...

    @abstractmethod
    def delete(self, entity_id: int) -> bool:
        """Remove an entity by its primary key.

        Args:
            entity_id: The unique identifier of the entity to delete.

        Returns:
            True if the entity was deleted, False if not found.
        """
        ...

    @abstractmethod
    def find_all(self, skip: int = 0, limit: int = 100) -> list[T]:
        """Retrieve a paginated list of all entities.

        Args:
            skip: Number of records to skip (for pagination).
            limit: Maximum number of records to return.

        Returns:
            A list of entities.
        """
        ...

    @abstractmethod
    def count(self) -> int:
        """Return the total number of entities.

        Returns:
            Total entity count.
        """
        ...

    @abstractmethod
    def exists(self, entity_id: int) -> bool:
        """Check if an entity exists by its primary key.

        Args:
            entity_id: The unique identifier to check.

        Returns:
            True if the entity exists, False otherwise.
        """
        ...
"""Repository interface definitions.

Defines abstract base classes and protocols for the data access layer,
ensuring consistent repository contracts across the application.
"""

from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar

T = TypeVar("T")


class RepositoryInterface(ABC, Generic[T]):
    """Abstract base class for all repositories.

    Defines the standard CRUD contract that all repository implementations
    must follow. Type parameter T represents the entity type.
    """

    @abstractmethod
    def find_by_id(self, entity_id: int) -> Optional[T]:
        """Retrieve an entity by its primary key.

        Args:
            entity_id: The unique identifier of the entity.

        Returns:
            The entity if found, None otherwise.
        """
        ...

    @abstractmethod
    def find_by_username(self, username: str) -> Optional[T]:
        """Retrieve an entity by its username.

        Args:
            username: The username to search for.

        Returns:
            The entity if found, None otherwise.
        """
        ...

    @abstractmethod
    def save(self, entity: T) -> T:
        """Persist a new entity to the data store.

        Args:
            entity: The entity instance to save.

        Returns:
            The saved entity with any generated fields populated.

        Raises:
            ValueError: If the entity data is invalid.
        """
        ...

    @abstractmethod
    def delete(self, entity_id: int) -> bool:
        """Remove an entity by its primary key.

        Args:
            entity_id: The unique identifier of the entity to delete.

        Returns:
            True if the entity was deleted, False if not found.
        """
        ...

    @abstractmethod
    def find_all(self, skip: int = 0, limit: int = 100) -> list[T]:
        """Retrieve a paginated list of all entities.

        Args:
            skip: Number of records to skip (for pagination).
            limit: Maximum number of records to return.

        Returns:
            A list of entities.
        """
        ...

    @abstractmethod
    def count(self) -> int:
        """Return the total number of entities.

        Returns:
            Total entity count.
        """
        ...

    @abstractmethod
    def exists(self, entity_id: int) -> bool:
        """Check if an entity exists by its primary key.

        Args:
            entity_id: The unique identifier to check.

        Returns:
            True if the entity exists, False otherwise.
        """
        ...
"""Repository interface definitions.

Defines abstract base classes and protocols for the data access layer,
ensuring consistent repository contracts across the application.
"""

from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar

T = TypeVar("T")


class RepositoryInterface(ABC, Generic[T]):
    """Abstract base class for all repositories.

    Defines the standard CRUD contract that all repository implementations
    must follow. Type parameter T represents the entity type.
    """

    @abstractmethod
    def find_by_id(self, entity_id: int) -> Optional[T]:
        """Retrieve an entity by its primary key.

        Args:
            entity_id: The unique identifier of the entity.

        Returns:
            The entity if found, None otherwise.
        """
        ...

    @abstractmethod
    def find_by_username(self, username: str) -> Optional[T]:
        """Retrieve an entity by its username.

        Args:
            username: The username to search for.

        Returns:
            The entity if found, None otherwise.
        """
        ...

    @abstractmethod
    def save(self, entity: T) -> T:
        """Persist a new entity to the data store.

        Args:
            entity: The entity instance to save.

        Returns:
            The saved entity with any generated fields populated.

        Raises:
            ValueError: If the entity data is invalid.
        """
        ...

    @abstractmethod
    def delete(self, entity_id: int) -> bool:
        """Remove an entity by its primary key.

        Args:
            entity_id: The unique identifier of the entity to delete.

        Returns:
            True if the entity was deleted, False if not found.
        """
        ...

    @abstractmethod
    def find_all(self, skip: int = 0, limit: int = 100) -> list[T]:
        """Retrieve a paginated list of all entities.

        Args:
            skip: Number of records to skip (for pagination).
            limit: Maximum number of records to return.

        Returns:
            A list of entities.
        """
        ...

    @abstractmethod
    def count(self) -> int:
        """Return the total number of entities.

        Returns:
            Total entity count.
        """
        ...

    @abstractmethod
    def exists(self, entity_id: int) -> bool:
        """Check if an entity exists by its primary key.

        Args:
            entity_id: The unique identifier to check.

        Returns:
            True if the entity exists, False otherwise.
        """
        ...
