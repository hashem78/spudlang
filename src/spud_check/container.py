from dependency_injector import containers, providers

from spud.di import Container as CoreContainer
from spud_check.type_checker import TypeChecker


class CheckContainer(containers.DeclarativeContainer):
    core = providers.Container(CoreContainer)

    pipeline = core.pipeline

    checker = providers.Singleton(TypeChecker)
