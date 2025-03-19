from typing import List, Set, Dict, Tuple, Optional


class Move:
    def __init__(self, model_move=None, log_move=None, objects=None, cost=0):
        self.model_move = model_move
        self.log_move = log_move
        self.objects = objects
        self.cost = cost


class LogMove(Move):
    def __init__(self, log_move, objects):
        calculated_cost = 1
        if objects:
            calculated_cost = len(objects)
        super().__init__(model_move=None, log_move=log_move, objects=objects, cost=calculated_cost)


class DefinedModelMove(Move):
    def __init__(self, model_move, objects: List[str], silent=False):
        self.silent = silent
        if silent == False:
            calculated_cost = 1
            if objects:
                calculated_cost = len(objects)
            super().__init__(model_move=model_move, log_move=None, objects=objects, cost=calculated_cost)
        else:
            super().__init__(model_move=model_move, log_move=None, objects=objects, cost=0.001)


class UndefinedModelMove(Move):
    def __init__(self, model_move: str, objects: Optional[List[str]], silent=False):
        self.silent = silent
        if silent == False:
            calculated_cost = 1
            if objects:
                calculated_cost = len(objects)
            super().__init__(model_move=model_move, log_move=None, objects=objects, cost=calculated_cost)
        else:
            super().__init__(model_move=model_move, log_move=None, objects=objects, cost=0.001)

    def define(self, objects: List[str]) -> DefinedModelMove:
        return DefinedModelMove(self.model_move, objects, self.silent)


class SynchronousMove(Move):
    def __init__(self, move, objects):
        super().__init__(model_move=move, log_move=move, objects=objects, cost=0)


class UndefinedSynchronousMove(Move):
    def __init__(self, move):
        super().__init__(model_move=move, log_move=move, objects=None, cost=0)
        self.px_preset = set()
        self.dejure_preset = set()

    def get_defined_sync_move(self, objects):
        return SynchronousMove(self.model_move, objects)




class Alignment:
    def __init__(self):
        self.moves = []
        self.object_types = None

    def __init__(self, moves: List[Move]):
        self.moves = moves

    def add_object_types(self, object_types):
        self.object_types = object_types

    def add_move(self, move: Move):
        self.moves.append(move)

    def add_moves(self, moves: List[Move]):
        self.moves = self.moves + moves

    def get_cost(self):
        total_cost = 0;
        for move in self.moves:
            total_cost += move.cost
        return total_cost


class TransitionSignature:
    """Class to represent the Signature of a transaction

    The in_cardinality attribute is a Dictionary. The keys are the object_types.
    The value represents how many ingoing arcs come from a place with the given object type.
    For the out_cardinality it is the same but with outgoing arcs.

    A transition from the process execution net and one from the preprocessed de jure net get a synchronous
    transition if their signature (without the move attribute) is equal.
    """

    def __init__(self, name: Optional[str] = None, in_cardinality: Optional[Dict[str, int]] = None,
                 out_cardinality: Optional[Dict[str, int]] = None, move: Optional[Move] = None):
        self.name = name
        self.in_cardinality = in_cardinality
        self.out_cardinality = out_cardinality
        self.move = move

    def __eq__(self, other):
        if not isinstance(other, TransitionSignature):
            return False
        if (self.name == other.name and self.in_cardinality == other.in_cardinality
                and self.out_cardinality == other.out_cardinality):
            return True
        else:
            return False


class DijkstraInfo:
    def __init__(self, previous_marking, move_to_this, cost=None):
        self.cost = cost  # None stands for infinite
        self.previous_marking = previous_marking
        self.move_to_this = move_to_this


class Binding:
    """
    Represents a Binding

    Property
    ----------
    binding: Dictionary that assigns a set of object instances to object types. The interpretation of that is that a
    binding will consume all the object_instances from preset places that are of the object type.
    """

    def __init__(self, binding_set: Dict[str, Set[str]]):
        self.binding = binding_set
