import logging

from CoachingBehaviourTree import config
from Policy.policy import Policy


class PolicyWrapper:
    """
    A class which acts as an interface between the raw policy and the behaviour tree. It can give the tree a behaviour
    or observation generated by the policy which is within a set of defined valid behaviours for a given state.
    ...
    Attributes
    ----------
    Goal Levels :type int
        6 different goal levels which correspond to stages in the interaction and the goal hierarchy of the racketware
        guide.
    Phases :type int
        2 different phases (start and end) which correspond respectively to either an intro or feedback sequence.
    Performance Levels :type int
        8 different performance levels which represent how the user did in their previous action.
    policy
        The policy we will query to obtain behaviours and observations.

    Methods
    -------
    get_behaviour(state, goal_level, performance, phase)
        Obtain a behaviour from the underlying policy and check it is valid in the current state of interaction.
    _get_valid_list(goal_level, performance, phase)
        Local method which creates the list of valid for each state of interaction.
    get_observation(state, behaviour)
        Obtain an observation from the underlying policy.
    """
    def __init__(self, belief=None, policy=None):
        self.policy = Policy(belief, policy)

    '''# Goal Levels
    PERSON_GOAL = 0
    SESSION_GOAL = 1
    EXERCISE_GOAL = 2
    SET_GOAL = 3
    ACTION_GOAL = 4

    # Phases
    PHASE_START = 0
    PHASE_END = 1

    # Performance Levels
    GOOD = 0            # Timing was within 0.5 secs either side of optimal
    FAST = 1            # Timing was <= optimal - 0.5secs
    SLOW = 2            # Timing was >= optimal + 0.5secs'''

    def get_behaviour(self, state, goal_level, performance, phase):
        """
        Obtain a behaviour from the underlying policy and check it is valid in the current state of interaction.
        :param state :type int: the previously observed state.
        :param goal_level :type int: the current goal level of the interaction.
        :param performance :type int: the performance of the user on their last action.
        :param phase :type int: the phase of the current goal level (either intro or feedback).
        :return behaviour :type int: the behaviour generated by the policy.
        """
        if goal_level == config.ACTION_GOAL:
            logging.debug("Action goal")
            logging.debug("performance = %s", performance)

        valid_behaviours = self._get_valid_list(goal_level, performance, phase)
        if goal_level == config.PERSON_GOAL and phase == config.PHASE_END:
            behaviour = config.A_END
        else:
            behaviour = self.policy.sample_action(state)
        # obs_behaviour = behaviour
        count = 0
        #if goal_level == config.ACTION_GOAL:
        debugString = "behaviour = ", behaviour, ". valid_behaviours: %s", valid_behaviours
        print(debugString)

        while not(behaviour in valid_behaviours):
            logging.debug("Not valid behaviour")
            if goal_level == config.ACTION_GOAL:     # If between shots, silence is an appropriate action so each time a
                print("behaviour == SILENCE")
                behaviour = config.A_SILENCE  # non-valid action is proposed, just use silence.
            else:
                if count <= 10:  # Only try this 10 times and if still no valid behaviour, try the next behaviour in the action sequence.
                    logging.debug("PolicyWrapper <= 10")
                    behaviour = self.policy.sample_action(state)
                else:
                    logging.debug("PolicyWrapper > 10")
                    # TODO: Remove this if else and figure out what's going on with centroids.
                    if behaviour == config.A_MANUALMANIPULATION_QUESTIONING:
                        behaviour = config.A_QUESTIONING
                    elif behaviour == config.A_MANUALMANIPULATION_PREINSTRUCTION \
                            or behaviour == config.A_PREINSTRUCTION_MANUALMANIPULATION:
                        behaviour = config.A_PREINSTRUCTION
                    elif behaviour == config.A_MANUALMANIPULATION_POSITIVEMODELING:
                        behaviour = config.A_POSITIVEMODELING
                    elif behaviour == config.A_MANUALMANIPULATION_CONCURRENTINSTRUCTIONNEGATIVE \
                            or behaviour == config.A_CONCURRENTINSTRUCTIONNEGATIVE_MANUALMANIPULATION:
                        behaviour = config.A_CONCURRENTINSTRUCTIONNEGATIVE
                    elif behaviour == config.A_MANUALMANIPULATION_CONCURRENTINSTRUCTIONPOSITIVE \
                            or behaviour == config.A_CONCURRENTINSTRUCTIONPOSITIVE_MANUALMANIPULATION:
                        behaviour = config.A_CONCURRENTINSTRUCTIONPOSITIVE
                    elif behaviour == config.A_MANUALMANIPULATION_CONSOLE:
                        behaviour = config.A_CONSOLE
                    elif behaviour == config.A_MANUALMANIPULATION_FIRSTNAME:
                        behaviour = config.A_FIRSTNAME
                    elif behaviour == config.A_MANUALMANIPULATION_HUSTLE:
                        behaviour = config.A_HUSTLE
                    elif behaviour == config.A_MANUALMANIPULATION_POSTINSTRUCTIONNEGATIVE \
                            or behaviour == config.A_POSTINSTRUCTIONNEGATIVE_MANUALMANIPULATION:
                        behaviour = config.A_POSTINSTRUCTIONNEGATIVE
                    elif behaviour == config.A_MANUALMANIPULATION_POSTINSTRUCTIONPOSITIVE \
                            or behaviour == config.A_POSTINSTRUCTIONPOSITIVE_MANUALMANIPULATION:
                        behaviour = config.A_POSTINSTRUCTIONPOSITIVE
                    elif behaviour == config.A_MANUALMANIPULATION_PRAISE:
                        behaviour = config.A_PRAISE
                    else:
                        if behaviour == config.A_END:  # If behaviour == end then start from start again.
                            behaviour = config.A_START
                        state = self.policy.sample_observation(action=behaviour, state=state)
                        behaviour = self.policy.sample_action(state)
                        count = 0
                count += 1
                debugString = "behaviour = ", behaviour, ". valid_behaviours: %s", valid_behaviours
                print(debugString)

        return behaviour  #, obs_behaviour

    def _get_valid_list(self, goal_level, performance, phase):
        """
        Local method which creates the list of valid for each state of interaction.
        :param goal_level :type int: the current goal level of the interaction.
        :param performance :type int: the performance of the user on their last action.
        :param phase :type int: the phase of the current goal level (either intro or feedback).
        :return valid_list :type list[int]: a list of valid behaviours in the current interaction state.
        """
        valid_list = []

        logging.debug('goal_level = ' + str(goal_level))
        # Person Goal
        if goal_level == config.PERSON_GOAL:
            logging.debug('Creating list for person goal')
            if phase == config.PHASE_START:
                valid_list.extend([config.A_PREINSTRUCTION, config.A_PREINSTRUCTION_FIRSTNAME])
            else:
                valid_list.append(config.A_END)

        # Session, Exercise and Set Goals will all have the same action categories (different individual actions)
        elif goal_level == config.SESSION_GOAL or goal_level == config.EXERCISE_GOAL or goal_level == config.SET_GOAL:
            valid_list.extend([config.A_POSTINSTRUCTIONPOSITIVE, config.A_POSTINSTRUCTIONNEGATIVE,
                               config.A_QUESTIONING, config.A_POSTINSTRUCTIONPOSITIVE_QUESTIONING,
                               config.A_POSTINSTRUCTIONPOSITIVE_FIRSTNAME,
                               config.A_POSTINSTRUCTIONNEGATIVE_QUESTIONING, config.A_QUESTIONING_FIRSTNAME,
                               config.A_POSTINSTRUCTIONNEGATIVE_FIRSTNAME,
                               config.A_QUESTIONING_POSITIVEMODELING, config.A_POSITIVEMODELING_QUESTIONING,
                               config.A_POSTINSTRUCTIONPOSITIVE_POSITIVE_MODELING,
                               config.A_POSTINSTRUCTIONPOSITIVE_NEGATIVE_MODELING,
                               config.A_POSTINSTRUCTIONNEGATIVE_POSITIVEMODELING,
                               config.A_POSTINSTRUCTIONNEGATIVE_NEGATIVEMODELING,
                               config.A_QUESTIONING_NEGATIVEMODELING,
                               config.A_POSITIVEMODELING_POSTINSTRUCTIONPOSITIVE,
                               config.A_NEGATIVEMODELING_POSTINSTRUCTIONNEGATIVE])
            if phase == config.PHASE_START:
                valid_list.extend([config.A_PREINSTRUCTION, config.A_PREINSTRUCTION_QUESTIONING,
                                   config.A_PREINSTRUCTION_FIRSTNAME,
                                   config.A_PREINSTRUCTION_POSITIVEMODELING,
                                   config.A_PREINSTRUCTION_NEGATIVEMODELING,
                                   config.A_POSITIVEMODELING_PREINSTRUCTION])
                if performance == config.GOOD:
                    valid_list.extend([config.A_PRAISE, config.A_PRAISE_FIRSTNAME,
                                       config.A_POSITIVEMODELING_PRAISE])
                    valid_list.extend([config.A_PRAISE, config.A_PRAISE_FIRSTNAME,
                                       config.A_POSITIVEMODELING_PRAISE])
                elif performance == config.SLOW or performance == config.FAST:
                    valid_list.extend([config.A_SCOLD, config.A_CONSOLE, config.A_SCOLD_FIRSTNAME,
                                       config.A_CONSOLE_FIRSTNAME])
            else:  # phase == config.PHASE_END
                if goal_level == config.SESSION_GOAL:
                    valid_list.append(config.A_END)
                if performance == config.GOOD:
                    valid_list.extend([config.A_PRAISE, config.A_PRAISE_FIRSTNAME,
                                       config.A_POSITIVEMODELING_PRAISE])
                elif performance == config.SLOW or performance == config.FAST:
                    valid_list.extend([config.A_SCOLD, config.A_CONSOLE, config.A_SCOLD_FIRSTNAME,
                                       config.A_CONSOLE_FIRSTNAME])

        # Action Goal (each shot in squash or repetition of exercise in rehab)
        else:  # goal_level == config.ACTION_GOAL:
            valid_list.extend([config.A_SILENCE, config.A_CONCURRENTINSTRUCTIONPOSITIVE,
                               config.A_QUESTIONING, config.A_POSITIVEMODELING, config.A_HUSTLE,
                               config.A_CONCURRENTINSTRUCTIONPOSITIVE_QUESTIONING,
                               config.A_CONCURRENTINSTRUCTIONPOSITIVE_FIRSTNAME,
                               config.A_QUESTIONING_FIRSTNAME, config.A_HUSTLE_FIRSTNAME,
                               config.A_CONCURRENTINSTRUCTIONPOSITIVE_POSITIVEMODELING,
                               config.A_POSITIVEMODELING_HUSTLE,
                               config.A_POSITIVEMODELING_CONCURRENTINSTRUCTIONPOSITIVE])
            # No phases in action goals, just a behaviour after each shot.
            if performance == config.GOOD:
                valid_list.extend([config.A_PRAISE, config.A_PRAISE_FIRSTNAME,
                                   config.A_CONCURRENTINSTRUCTIONPOSITIVE_PRAISE,
                                   config.A_POSITIVEMODELING_PRAISE])
            elif performance == config.SLOW or performance == config.FAST:
                valid_list.extend([config.A_CONCURRENTINSTRUCTIONNEGATIVE, config.A_NEGATIVEMODELING,
                                   config.A_SCOLD, config.A_CONSOLE,
                                   config.A_QUESTIONING_NEGATIVEMODELING, config.A_SCOLD_POSITIVEMODELING,
                                   config.A_SCOLD_FIRSTNAME, config.A_CONSOLE_FIRSTNAME,
                                   config.A_CONCURRENTINSTRUCTIONNEGATIVE_NEGATIVEMODELING,
                                   config.A_CONCURRENTINSTRUCTIONNEGATIVE_FIRSTNAME,])

        return valid_list

    def get_observation(self, state, behaviour):
        """
        Obtain an observation from the underlying policy.
        :param state :type int: the previously observed state.
        :param behaviour :type int: the previous behaviour generated by the policy.
        :return:type int: the observation of which state we have moved to, generated by the policy.
        """
        return self.policy.sample_observation(state, behaviour)

    def get_matrix(self):
        return self.policy.get_matrix()

    def update_matrix(self, state, action, updatedValue):
        self.policy.update(state, action, updatedValue)
        return self.policy.get_matrix()
