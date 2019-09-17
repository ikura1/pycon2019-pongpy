import os

from pongpy.controllers.ball import Ball
from pongpy.interfaces.team import Team
from pongpy.models.game_info import GameInfo
from pongpy.models.state import State
from pongpy.models.pos import Pos


PLAYER_NAME = os.environ["PLAYER_NAME"]


def predict_ball_y(info: GameInfo, pos1: Pos, pos2: Pos, pred_x):
    x1, y1 = pos1
    x2, y2 = pos2
    vx, vy = x2 - x1, y2 - y1
    ball = Ball(info.ball_size, pos2, vx, vy)
    if vx > 0:
        return y2
    while ball.pos.x > pred_x + info.bar_width:
        ball = update(info, ball)
    return ball.pos.y


def is_contact(ball_pos, bar_pos, size, width):
    # ボールの接触判定
    size = size // 2
    width = width // 2
    if bar_pos.x - width > ball_pos.x > bar_pos.x + width:
        # ボールがBARと同じxに存在するか
        return False
    if ball_pos.y - size > ball_pos.y > bar_pos.y + size:
        # ボールがBARと同じyに存在するか
        return False
    return True


def update(info, ball):
    # ボールの動作コピペ
    ball_pos = ball.updated()
    ball.pos = ball_pos

    ball_x, ball_y = ball_pos
    if ball_pos.y <= 0:
        ball.pos = Pos(ball_pos.x, -ball_pos.y)
        ball.vy *= -1
    if ball_pos.y >= info.height:
        ball.pos = Pos(ball_pos.x, info.height - (ball_pos.y - info.height))
        ball.vy *= -1
    return ball


class ChallengerTeam(Team):
    prev_ball_pos = None

    @property
    def name(self) -> str:
        return PLAYER_NAME

    def atk_action(self, info: GameInfo, state: State) -> int:
        """
        前衛の青色のバーをコントロールします。
        * barのposは真ん中
        """
        atk_x, atk_y = state.mine_team.atk_pos
        ball_x, ball_y = state.ball_pos

        if self.prev_ball_pos:
            prev_ball_x, prev_ball_y = self.prev_ball_pos
            pred_ball_y = predict_ball_y(
                info, self.prev_ball_pos, state.ball_pos, atk_x
            )
            self.prev_ball_pos = state.ball_pos
            direction = pred_ball_y - atk_y
        else:
            direction = ball_y - atk_y

        if direction == 0:
            return 0
        move_point = info.atk_return_limit if direction > 0 else -info.atk_return_limit
        return move_point

    def def_action(self, info: GameInfo, state: State) -> int:
        """
        後衛のオレンジ色のバーをコントロールします。
        """
        # FIXME: 移動速度が低くて木偶になってる
        # TODO: atkの位置で移動制限するかな
        def_x, def_y = state.mine_team.def_pos
        ball_x, ball_y = state.ball_pos

        if self.prev_ball_pos and state.ball_pos != self.prev_ball_pos:
            prev_ball_x, prev_ball_y = self.prev_ball_pos
            pred_ball_y = predict_ball_y(
                info, self.prev_ball_pos, state.ball_pos, def_x
            )
            direction = pred_ball_y - def_y
        else:
            direction = ball_y - def_y

        self.prev_ball_pos = state.ball_pos
        if direction == 0:
            return 0
        move_point = info.def_return_limit if direction > 0 else -info.def_return_limit
        return move_point
