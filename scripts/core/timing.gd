class_name Timing
## Hard delays from the combat-feel timing table.
## A player basic attack blocks for about 0.95 s (inside 0.8–1.2).
## A typical monster basic attack (damage frame 2) matches that.
## A safe hop with no roll is 2.5 s.

const FLOATER_QUEUE := 0.25
const SAVING_THROW := 0.35
const MULTI_TARGET_GAP := 0.2
const SKILL_WAIT_BEFORE_CB := 0.25
const CONDITION_DAMAGE := 0.25
const CONDITION_GAP := 0.3
const PASSIVE_POPUP := 0.2
const CRIT_HOLD := 0.25
const COUNTER := 0.25
const COUNTER_ATTACK := 0.2
const PLAYER_NEXT_TURN := 0.3
const MONSTER_NEXT_TURN := 0.25
const MONSTER_WINDUP := 0.25
const MONSTER_ATTACK_FPS := 5.0
const HIT_PUNCH := 0.3
const HIT_PUNCH_AMOUNT := 0.2
const PUNCH_PIXELS := 6
const HIT_BLINK_IN := 0.1
const HIT_BLINK_OUT := 0.1
const HP_TWEEN := 0.5
const XP_TWEEN := 2.0
const DEATH_BLINK_OFF := 0.05
const DEATH_BLINKS := 6
const VICTORY_DELAY := 2.0
const LOCATION_BANNER := 2.0
const BATTLE_INTRO := 1.0
const TERRAIN_INTRO_MIN := 1.5
const TRAVEL_TIME := 4.0
const HOP_APPROACH := 2.0
const HOP_SPRINT := 0.5
const TRAVEL_ROLL_SPIN := 0.9
const TRAVEL_ROLL_VISIBLE := 1.9
const PARTY_DIE_SPIN := 0.2
const PARTY_DIE_SPIN_FLEE := 0.4
const PARTY_DIE_AFTER := 0.2
const PARTY_DIE_BONUS := 0.1
const PARTY_DIE_GAP := 0.1
const PARTY_ROLL_END_HOLD := 1.0
const CHICKEN_MOVE := 1.8
const CHICKEN_SFX_AT := 1.1
const UNTARGET_GREY := 0.3
const TARGET_FLICKER_ON := 0.3
const TARGET_FLICKER_OFF := 0.3
const PLAYER_RISE_PX := 10
const PLAYER_ATTACK_WINDUP := 0.25
const PLAYER_ATTACK_TO_HIT := 0.20
const LOW_LEVEL_GOLD_CUTOFF := 8


static func monster_time_to_damage(damage_frame: int) -> float:
	return float(maxi(1, damage_frame) - 1) / MONSTER_ATTACK_FPS


static func death_blink_seconds() -> float:
	var total := 0.0
	for i in range(DEATH_BLINKS, 0, -1):
		total += DEATH_BLINK_OFF
		total += DEATH_BLINK_OFF * float(i)
	return total


static func player_basic_attack_seconds() -> float:
	# Wind-up, time-to-hit, then the HP tween. Punch (0.3) and blink (0.2)
	# run inside the tween, so they do not add. Crit hold is extra.
	return PLAYER_ATTACK_WINDUP + PLAYER_ATTACK_TO_HIT + HP_TWEEN


static func monster_basic_attack_seconds(damage_frame: int = 2) -> float:
	return MONSTER_WINDUP + monster_time_to_damage(damage_frame) + HP_TWEEN


static func safe_hop_seconds() -> float:
	return HOP_APPROACH + HOP_SPRINT


static func travel_roll_lead() -> float:
	# The roll starts this long before the midpoint so it resolves on arrival.
	return maxf(0.0, HOP_APPROACH - TRAVEL_ROLL_VISIBLE)
