import os

from pongpy.interfaces.team import Team
from pongpy.models.game_info import GameInfo
from pongpy.models.state import State
from pongpy.models.pos import Pos


PLAYER_NAME = os.environ["PLAYER_NAME"]


class ChallengerTeam(Team):
    prov_ball_pos = None

    @property
    def name(self) -> str:
        return PLAYER_NAME

    def atk_action(self, info: GameInfo, state: State) -> int:
        """
        前衛の青色のバーをコントロールします。
        フレームごとに移動する
        * 正数の場合
            * 下に移動する
        * 負数の場合
            * 上に移動する
        ***

        * 前のボール保持
        * 移動方向の判定
        * 壁での反射での計算
        * atkとdefの位置関係をどうするか
        * barの位置情報が上か下か
        """
        # width
        # height
        # info.atk_size
        # info.ball_size
        # info.atk_return_limit
        direction = (state.ball_pos.y - state.mine_team.atk_pos.y) > 0
        self.prov_ball_pos = state.ball_pos
        return info.atk_return_limit if direction else -info.atk_return_limit

    def def_action(self, info: GameInfo, state: State) -> int:
        """
        後衛のオレンジ色のバーをコントロールします。
        """
        direction = (state.ball_pos.y - state.mine_team.def_pos.y) > 0
        self.prov_ball_pos = state.ball_pos
        return info.def_return_limit if direction else -info.def_return_limit
