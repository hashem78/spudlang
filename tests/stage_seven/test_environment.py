from spud.core.environment import Environment


class TestWithBinding:
    def test_adds_binding(self):
        env: Environment[int] = Environment()
        result = env.with_binding("x", 42)
        assert result.lookup("x") == 42

    def test_returns_new_environment(self):
        env: Environment[int] = Environment()
        result = env.with_binding("x", 42)
        assert result is not env

    def test_original_unchanged(self):
        env: Environment[int] = Environment()
        env.with_binding("x", 42)
        assert env.lookup("x") is None

    def test_overwrites_existing_key(self):
        env: Environment[int] = Environment()
        env = env.with_binding("x", 1)
        env = env.with_binding("x", 2)
        assert env.lookup("x") == 2

    def test_chaining_multiple_calls(self):
        env: Environment[int] = Environment()
        env = env.with_binding("a", 1).with_binding("b", 2).with_binding("c", 3)
        assert env.lookup("a") == 1
        assert env.lookup("b") == 2
        assert env.lookup("c") == 3

    def test_preserves_existing_bindings(self):
        env: Environment[int] = Environment()
        env = env.with_binding("x", 10)
        env = env.with_binding("y", 20)
        assert env.lookup("x") == 10
        assert env.lookup("y") == 20


class TestChild:
    def test_creates_new_environment(self):
        env: Environment[int] = Environment()
        child = env.child()
        assert child is not env

    def test_parent_is_set(self):
        env: Environment[int] = Environment()
        child = env.child()
        assert child.parent is env

    def test_child_starts_with_no_own_bindings(self):
        env: Environment[int] = Environment()
        env = env.with_binding("x", 1)
        child = env.child()
        assert not child.contains("x")

    def test_child_of_child_has_correct_parent(self):
        env: Environment[int] = Environment()
        child = env.child()
        grandchild = child.child()
        assert grandchild.parent is child


class TestLookup:
    def test_finds_in_current_scope(self):
        env: Environment[int] = Environment()
        env = env.with_binding("x", 99)
        assert env.lookup("x") == 99

    def test_walks_parent_chain(self):
        env: Environment[int] = Environment()
        env = env.with_binding("x", 7)
        child = env.child()
        assert child.lookup("x") == 7

    def test_walks_grandparent_chain(self):
        env: Environment[int] = Environment()
        env = env.with_binding("x", 3)
        child = env.child()
        grandchild = child.child()
        assert grandchild.lookup("x") == 3

    def test_returns_none_when_not_found(self):
        env: Environment[int] = Environment()
        assert env.lookup("missing") is None

    def test_returns_none_when_not_found_with_parent(self):
        env: Environment[int] = Environment()
        child = env.child()
        assert child.lookup("missing") is None

    def test_child_binding_shadows_parent(self):
        env: Environment[int] = Environment()
        env = env.with_binding("x", 1)
        child = env.child().with_binding("x", 2)
        assert child.lookup("x") == 2

    def test_parent_unchanged_when_child_has_shadowing_binding(self):
        env: Environment[int] = Environment()
        env = env.with_binding("x", 1)
        child = env.child().with_binding("x", 2)
        assert env.lookup("x") == 1
        assert child.lookup("x") == 2


class TestContains:
    def test_finds_in_current_scope(self):
        env: Environment[int] = Environment()
        env = env.with_binding("x", 5)
        assert env.contains("x")

    def test_does_not_find_in_parent(self):
        env: Environment[int] = Environment()
        env = env.with_binding("x", 5)
        child = env.child()
        assert not child.contains("x")

    def test_returns_false_when_absent(self):
        env: Environment[int] = Environment()
        assert not env.contains("x")

    def test_does_not_find_in_grandparent(self):
        env: Environment[int] = Environment()
        env = env.with_binding("x", 5)
        grandchild = env.child().child()
        assert not grandchild.contains("x")
