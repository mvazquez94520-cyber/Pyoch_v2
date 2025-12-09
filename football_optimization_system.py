"""
Football Club Optimization System with Recruitment Features

This system provides:
- Player selection for matches
- Form prediction and injury risk assessment
- Optimal 11 selection based on opponent and objectives
- Recruitment recommendations with visual profiles
"""

import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import numpy as np


class Player:
    """Represents a football player with statistics and attributes"""
    
    def __init__(self, name: str, position: str, age: int, overall_rating: int):
        self.name = name
        self.position = position  # GK, DEF, MID, FWD
        self.age = age
        self.overall_rating = overall_rating
        
        # Performance metrics
        self.form = 7.5  # Current form (1-10 scale)
        self.fitness = 8.0  # Physical condition (1-10 scale)
        self.injury_risk = 0.2  # Probability of injury (0-1 scale)
        self.motivation = 8.5  # Motivation level (1-10 scale)
        
        # Technical stats
        self.pass_accuracy = 0.85
        self.shooting = 0.78
        self.defending = 0.72
        self.pace = 0.80
        self.stamina = 0.85
        
        # Historical data
        self.recent_matches = []
        self.performance_trend = 0.0  # Positive/negative trend
        self.minutes_played = 0
        self.goals = 0
        self.assists = 0
        self.clean_sheets = 0  # For goalkeepers/defenders
        

class MatchAnalyzer:
    """Analyzes upcoming matches and recommends team selection"""
    
    def __init__(self, team_players: List[Player]):
        self.players = team_players
        self.opponent_analysis = {}
        
    def analyze_opponent(self, opponent_strengths: Dict[str, float], 
                        opponent_weaknesses: Dict[str, float]) -> Dict:
        """Analyze opponent characteristics to inform team selection"""
        self.opponent_analysis = {
            'strengths': opponent_strengths,
            'weaknesses': opponent_weaknesses
        }
        return self.opponent_analysis
    
    def calculate_player_match_fitness(self, player: Player, 
                                     match_importance: float = 0.5) -> float:
        """Calculate how fit a player is for a specific match"""
        # Base fitness calculation
        base_fitness = (
            player.form * 0.3 +
            player.fitness * 0.25 +
            player.motivation * 0.25 +
            (10 - player.injury_risk * 10) * 0.2
        )
        
        # Adjust for match importance and recent play
        if player.minutes_played > 180:  # Recently played many minutes
            base_fitness *= 0.9  # Reduce for fatigue
        
        # Adjust for match importance
        if match_importance > 0.7:  # Important match
            base_fitness += 0.3 * (match_importance - 0.5)
        
        return min(base_fitness, 10.0)
    
    def select_best_11(self, formation: str = "4-3-3", 
                      match_objective: str = "win",
                      opponent_analysis: Dict = None) -> Dict:
        """Select the optimal 11 players for the match"""
        
        # Group players by position
        positions = {
            'GK': [],
            'DEF': [],
            'MID': [],
            'FWD': []
        }
        
        for player in self.players:
            positions[player.position].append(player)
        
        # Define formation requirements
        formation_map = {
            "4-3-3": {"GK": 1, "DEF": 4, "MID": 3, "FWD": 3},
            "4-4-2": {"GK": 1, "DEF": 4, "MID": 4, "FWD": 2},
            "3-5-2": {"GK": 1, "DEF": 3, "MID": 5, "FWD": 2},
            "5-3-2": {"GK": 1, "DEF": 5, "MID": 3, "FWD": 2}
        }
        
        required_positions = formation_map.get(formation, formation_map["4-3-3"])
        
        selected_team = {
            'formation': formation,
            'starting_11': [],
            'bench': []
        }
        
        # Select best players for each position
        for pos, count in required_positions.items():
            eligible_players = positions[pos]
            
            # Calculate match fitness for eligible players
            player_fitness_scores = [
                (p, self.calculate_player_match_fitness(p))
                for p in eligible_players
            ]
            
            # Sort by fitness score (descending)
            player_fitness_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Add top players to starting 11
            for i in range(min(count, len(player_fitness_scores))):
                selected_team['starting_11'].append({
                    'player': player_fitness_scores[i][0],
                    'position': pos,
                    'fitness_score': round(player_fitness_scores[i][1], 2),
                    'role': self.determine_role(pos, i, len(selected_team['starting_11']))
                })
        
        # Add remaining players to bench
        used_names = [p['player'].name for p in selected_team['starting_11']]
        for pos, players in positions.items():
            for player in players:
                if player.name not in used_names:
                    selected_team['bench'].append({
                        'player': player,
                        'position': pos,
                        'fitness_score': round(self.calculate_player_match_fitness(player), 2)
                    })
        
        # Sort bench by fitness score
        selected_team['bench'].sort(key=lambda x: x['fitness_score'], reverse=True)
        
        return selected_team
    
    def determine_role(self, position: str, index: int, total_count: int) -> str:
        """Determine specific role for a player in their position"""
        if position == "GK":
            return "Starting GK"
        elif position == "DEF":
            roles = ["Center-back", "Right-back", "Left-back", "Sweeper"]
            return roles[index % len(roles)]
        elif position == "MID":
            roles = ["Defensive Mid", "Central Mid", "Attacking Mid", "Wide Mid"]
            return roles[index % len(roles)]
        elif position == "FWD":
            roles = ["Striker", "Second Striker", "Winger"]
            return roles[index % len(roles)]
        
        return f"{position} {index+1}"


class PlayerAnalyzer:
    """Analyzes individual player performance and predicts future form"""
    
    def __init__(self, players: List[Player]):
        self.players = players
    
    def assess_current_form(self, player: Player) -> Dict:
        """Assess current form and predict future performance"""
        # Calculate form trends
        recent_performance = player.form
        fitness_level = player.fitness
        injury_risk = player.injury_risk
        
        # Predict next 4 weeks
        predictions = []
        current_date = datetime.now()
        
        for week in range(1, 5):
            date = current_date + timedelta(weeks=week)
            
            # Simulate form changes based on various factors
            predicted_form = recent_performance
            predicted_form -= injury_risk * 0.5  # Risk factor
            predicted_form += (fitness_level - 7) * 0.1  # Fitness impact
            
            # Add some randomness
            predicted_form += np.random.normal(0, 0.2)
            predicted_form = max(1, min(10, predicted_form))  # Clamp to 1-10
            
            predictions.append({
                'date': date.strftime('%Y-%m-%d'),
                'predicted_form': round(predicted_form, 2),
                'risk_level': 'High' if injury_risk > 0.3 else 'Medium' if injury_risk > 0.15 else 'Low'
            })
        
        return {
            'current_form': player.form,
            'fitness_level': player.fitness,
            'injury_risk': injury_risk,
            'motivation': player.motivation,
            'predictions': predictions,
            'trend': 'Improving' if player.performance_trend > 0 else 'Declining' if player.performance_trend < 0 else 'Stable'
        }
    
    def generate_recruitment_profile(self, player: Player) -> Dict:
        """Generate a recruitment profile for a player"""
        form_assessment = self.assess_current_form(player)
        
        return {
            'name': player.name,
            'position': player.position,
            'age': player.age,
            'overall_rating': player.overall_rating,
            'current_form': form_assessment['current_form'],
            'fitness_level': form_assessment['fitness_level'],
            'injury_risk': form_assessment['injury_risk'],
            'motivation': form_assessment['motivation'],
            'performance_trend': form_assessment['trend'],
            'strengths': self.identify_strengths(player),
            'weaknesses': self.identify_weaknesses(player),
            'potential': self.estimate_potential(player),
            'compatibility_score': self.calculate_compatibility(player),
            'recruitment_priority': self.calculate_recruitment_priority(player)
        }
    
    def identify_strengths(self, player: Player) -> List[str]:
        """Identify player's strengths based on stats"""
        strengths = []
        
        if player.pass_accuracy > 0.85:
            strengths.append("Passing")
        if player.shooting > 0.75:
            strengths.append("Shooting")
        if player.defending > 0.75:
            strengths.append("Defending")
        if player.pace > 0.80:
            strengths.append("Pace")
        if player.stamina > 0.85:
            strengths.append("Stamina")
        if player.form > 8.0:
            strengths.append("Current Form")
        if player.fitness > 8.5:
            strengths.append("Fitness")
        
        return strengths if strengths else ["Well-rounded player"]
    
    def identify_weaknesses(self, player: Player) -> List[str]:
        """Identify player's weaknesses based on stats"""
        weaknesses = []
        
        if player.pass_accuracy < 0.70:
            weaknesses.append("Passing")
        if player.shooting < 0.60:
            weaknesses.append("Shooting")
        if player.defending < 0.60:
            weaknesses.append("Defending")
        if player.pace < 0.65:
            weaknesses.append("Pace")
        if player.stamina < 0.70:
            weaknesses.append("Stamina")
        if player.form < 6.0:
            weaknesses.append("Current Form")
        if player.fitness < 7.0:
            weaknesses.append("Fitness")
        if player.injury_risk > 0.3:
            weaknesses.append("Injury Prone")
        
        return weaknesses if weaknesses else ["No major weaknesses"]
    
    def estimate_potential(self, player: Player) -> float:
        """Estimate player's potential on a 1-10 scale"""
        # Younger players generally have higher potential
        age_factor = max(0, 1 - (player.age - 20) / 25)
        
        # Consider current rating and form
        potential = (player.overall_rating / 10) * 0.4 + \
                   player.form * 0.3 + \
                   (10 - player.injury_risk * 10) * 0.2 + \
                   age_factor * 0.1
        
        return min(10.0, max(1.0, potential))
    
    def calculate_compatibility(self, player: Player) -> float:
        """Calculate how well the player fits the team"""
        # This would normally consider team tactics and needs
        compatibility = (
            player.overall_rating * 0.3 +
            player.form * 0.25 +
            (10 - player.injury_risk * 10) * 0.2 +
            player.motivation * 0.25
        )
        return min(10.0, max(1.0, compatibility))
    
    def calculate_recruitment_priority(self, player: Player) -> str:
        """Calculate recruitment priority level"""
        potential = self.estimate_potential(player)
        form = player.form
        injury_risk = player.injury_risk
        
        score = potential * 0.4 + form * 0.3 + (10 - injury_risk * 10) * 0.3
        
        if score >= 8.0:
            return "High Priority"
        elif score >= 6.0:
            return "Medium Priority"
        else:
            return "Low Priority"


class TacticalAdvisor:
    """Provides tactical recommendations for matches"""
    
    def recommend_formation(self, opponent_analysis: Dict) -> str:
        """Recommend the best formation against the opponent"""
        strengths = opponent_analysis.get('strengths', {})
        weaknesses = opponent_analysis.get('weaknesses', {})
        
        # If opponent is weak in defense, recommend attacking formation
        if weaknesses.get('defense', 0) > 0.6:
            return "4-3-3"  # Attacking formation
        
        # If opponent is strong in attack, recommend defensive formation
        if strengths.get('attack', 0) > 0.7:
            return "5-3-2"  # Defensive formation
        
        # Default balanced formation
        return "4-4-2"
    
    def suggest_key_duels(self, opponent_analysis: Dict) -> List[Dict]:
        """Suggest key player duels to focus on"""
        duels = []
        
        # Identify opponent's strongest players to neutralize
        for area, strength in opponent_analysis.get('strengths', {}).items():
            if strength > 0.7:  # Strong in this area
                duels.append({
                    'target_area': area,
                    'recommendation': f'Double-mark opponents in {area}',
                    'priority': 'High'
                })
        
        # Identify opponent's weak areas to exploit
        for area, weakness in opponent_analysis.get('weaknesses', {}).items():
            if weakness > 0.6:  # Weak in this area
                duels.append({
                    'target_area': area,
                    'recommendation': f'Attack through {area}',
                    'priority': 'High'
                })
        
        return duels if duels else [{'target_area': 'N/A', 'recommendation': 'Focus on general game plan', 'priority': 'Medium'}]


class FootballOptimizationSystem:
    """Main class that orchestrates the entire optimization system"""
    
    def __init__(self, players: List[Player]):
        self.players = players
        self.match_analyzer = MatchAnalyzer(players)
        self.player_analyzer = PlayerAnalyzer(players)
        self.tactical_advisor = TacticalAdvisor()
    
    def generate_match_report(self, opponent_strengths: Dict[str, float], 
                            opponent_weaknesses: Dict[str, float],
                            match_importance: float = 0.5,
                            formation: str = None) -> Dict:
        """Generate a complete match report"""
        
        # Analyze opponent
        opponent_analysis = self.match_analyzer.analyze_opponent(
            opponent_strengths, opponent_weaknesses
        )
        
        # Recommend formation if not provided
        if not formation:
            formation = self.tactical_advisor.recommend_formation(opponent_analysis)
        
        # Select best 11
        team_selection = self.match_analyzer.select_best_11(
            formation=formation,
            match_objective="win",
            opponent_analysis=opponent_analysis
        )
        
        # Generate tactical recommendations
        key_duels = self.tactical_advisor.suggest_key_duels(opponent_analysis)
        
        # Assess player risks
        player_risks = {}
        for player in self.players:
            form_assessment = self.player_analyzer.assess_current_form(player)
            player_risks[player.name] = {
                'form': form_assessment['current_form'],
                'fitness': form_assessment['fitness_level'],
                'injury_risk': form_assessment['injury_risk'],
                'trend': form_assessment['trend']
            }
        
        return {
            'team_selection': team_selection,
            'formation': formation,
            'opponent_analysis': opponent_analysis,
            'key_duels': key_duels,
            'player_risks': player_risks,
            'tactical_recommendations': self.generate_tactical_notes(team_selection, opponent_analysis)
        }
    
    def generate_tactical_notes(self, team_selection: Dict, opponent_analysis: Dict) -> List[str]:
        """Generate tactical notes for the match"""
        notes = []
        
        # Formation-specific instructions
        if team_selection['formation'] == "4-3-3":
            notes.append("Press high and wide, utilize wingbacks for width")
        elif team_selection['formation'] == "4-4-2":
            notes.append("Maintain compact shape, use overlapping fullbacks")
        elif team_selection['formation'] == "3-5-2":
            notes.append("Use wingbacks for attacks, midfield numerical advantage")
        
        # Exploit opponent weaknesses
        weaknesses = opponent_analysis.get('weaknesses', {})
        for weakness, severity in weaknesses.items():
            if severity > 0.6:
                notes.append(f"Exploit opponent's {weakness} weakness ({severity*100}% severity)")
        
        # Counter opponent strengths
        strengths = opponent_analysis.get('strengths', {})
        for strength, severity in strengths.items():
            if severity > 0.7:
                notes.append(f"Neutralize opponent's {strength} strength ({severity*100}% strength)")
        
        return notes
    
    def generate_recruitment_report(self) -> List[Dict]:
        """Generate a recruitment report for potential signings"""
        prospects = []
        
        for player in self.players:
            profile = self.player_analyzer.generate_recruitment_profile(player)
            prospects.append(profile)
        
        # Sort by recruitment priority
        priority_map = {"High Priority": 3, "Medium Priority": 2, "Low Priority": 1}
        prospects.sort(key=lambda x: priority_map[x['recruitment_priority']], reverse=True)
        
        return prospects


def create_sample_players() -> List[Player]:
    """Create sample players for demonstration"""
    players = [
        Player("Thibaut Courtois", "GK", 31, 92),
        Player("Virgil van Dijk", "DEF", 32, 89),
        Player("Trent Alexander-Arnold", "DEF", 25, 87),
        Player("Andrew Robertson", "DEF", 29, 88),
        Player("Joel Matip", "DEF", 32, 82),
        Player("Fabinho", "MID", 30, 84),
        Player("Jordan Henderson", "MID", 33, 83),
        Player("Alexis Mac Allister", "MID", 25, 85),
        Player("Mohamed Salah", "FWD", 31, 90),
        Player("Darwin Núñez", "FWD", 24, 83),
        Player("Luis Díaz", "FWD", 26, 86),
        Player("Dominik Szoboszlai", "MID", 23, 84),
        Player("Alisson", "GK", 31, 88),
        Player("Ibrahima Konaté", "DEF", 24, 85),
        Player("Kostas Tsimikas", "DEF", 27, 79)
    ]
    
    # Set custom attributes for demonstration
    players[0].form = 8.7
    players[0].fitness = 8.8
    players[0].injury_risk = 0.1
    players[0].pass_accuracy = 0.82
    
    players[1].form = 8.5
    players[1].fitness = 8.9
    players[1].injury_risk = 0.15
    players[1].defending = 0.92
    
    players[8].form = 9.0
    players[8].shooting = 0.88
    players[8].pace = 0.91
    players[8].injury_risk = 0.25
    
    return players


def main():
    """Main function demonstrating the system"""
    print("Football Club Optimization System with Recruitment")
    print("=" * 55)
    
    # Create sample players
    players = create_sample_players()
    system = FootballOptimizationSystem(players)
    
    # Define opponent analysis
    opponent_strengths = {
        'attack': 0.8,
        'midfield': 0.6,
        'defense': 0.7
    }
    
    opponent_weaknesses = {
        'defense': 0.7,  # Weak in defense
        'set_pieces': 0.6,
        'right_flank': 0.8  # Very weak on right flank
    }
    
    # Generate match report
    print("\n1. Generating Match Report...")
    match_report = system.generate_match_report(
        opponent_strengths=opponent_strengths,
        opponent_weaknesses=opponent_weaknesses,
        match_importance=0.8
    )
    
    print(f"\nRecommended Formation: {match_report['formation']}")
    print("\nStarting 11:")
    for i, player_info in enumerate(match_report['team_selection']['starting_11']):
        player = player_info['player']
        print(f"  {i+1}. {player.name} ({player.position}) - {player_info['role']} "
              f"[Fitness: {player_info['fitness_score']}]")
    
    print("\nKey Tactical Duels:")
    for duel in match_report['key_duels']:
        print(f"  - {duel['recommendation']} (Priority: {duel['priority']})")
    
    # Generate recruitment report
    print("\n2. Generating Recruitment Report...")
    recruitment_report = system.generate_recruitment_report()
    
    print("\nTop Recruitment Targets:")
    for i, prospect in enumerate(recruitment_report[:5]):  # Top 5 targets
        print(f"  {i+1}. {prospect['name']} ({prospect['position']}) - "
              f"Priority: {prospect['recruitment_priority']}")
        print(f"     Overall: {prospect['overall_rating']}, "
              f"Potential: {prospect['potential']:.1f}, "
              f"Compatibility: {prospect['compatibility_score']:.1f}")
        print(f"     Strengths: {', '.join(prospect['strengths'])}")
        print(f"     Weaknesses: {', '.join(prospect['weaknesses'])}")
    
    # Show player form predictions
    print("\n3. Player Form Predictions (Next 4 Weeks):")
    for player in players[:3]:  # Show for first 3 players
        form_assessment = system.player_analyzer.assess_current_form(player)
        print(f"\n{player.name}:")
        print(f"  Current Form: {form_assessment['current_form']}, "
              f"Trend: {form_assessment['trend']}, "
              f"Injury Risk: {'High' if form_assessment['injury_risk'] > 0.3 else 'Low'}")
        print("  Predictions:")
        for pred in form_assessment['predictions']:
            print(f"    {pred['date']}: {pred['predicted_form']} "
                  f"(Risk: {pred['risk_level']})")


if __name__ == "__main__":
    main()