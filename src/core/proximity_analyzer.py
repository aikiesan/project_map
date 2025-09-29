"""
CP2B Maps V2 - Professional Proximity Analysis Core
Advanced proximity analysis with biogas plant location optimization
"""

import math
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Union
import streamlit as st

# Geospatial imports with error handling
try:
    import geopandas as gpd
    from shapely.geometry import Point, Polygon
    HAS_GEOSPATIAL = True
except ImportError:
    HAS_GEOSPATIAL = False

from config.settings import settings
from src.utils.logging_config import get_logger
from src.core.geospatial_analysis import get_geospatial_analyzer
from src.data.loaders.mapbiomas_loader import get_mapbiomas_loader

logger = get_logger(__name__)


class ProximityAnalyzer:
    """
    Professional proximity analysis with biogas plant optimization
    Features: Catchment area analysis, optimal location finding, multi-criteria evaluation
    """

    def __init__(self):
        """Initialize ProximityAnalyzer"""
        self.logger = get_logger(self.__class__.__name__)
        self.geospatial_analyzer = get_geospatial_analyzer()
        self.mapbiomas_loader = get_mapbiomas_loader()

        if not HAS_GEOSPATIAL:
            self.logger.warning("Geospatial libraries not available - limited functionality")

    def validate_coordinates(self, lat: float, lon: float, radius_km: float) -> Tuple[bool, str]:
        """
        Validate proximity analysis coordinates

        Args:
            lat: Latitude
            lon: Longitude
            radius_km: Analysis radius in kilometers

        Returns:
            Tuple of (is_valid, message)
        """
        try:
            # Latitude validation
            if not (-90 <= lat <= 90):
                return False, f"Invalid latitude: {lat}. Must be between -90 and 90."

            # Longitude validation
            if not (-180 <= lon <= 180):
                return False, f"Invalid longitude: {lon}. Must be between -180 and 180."

            # Radius validation
            if not (0 < radius_km <= 200):
                return False, f"Invalid radius: {radius_km}. Must be between 0 and 200 km."

            # São Paulo state bounds check (optional but helpful)
            if not self._is_within_sao_paulo_region(lat, lon):
                self.logger.warning(f"Coordinates ({lat}, {lon}) outside São Paulo region")
                return True, f"Warning: Coordinates outside São Paulo region but valid"

            return True, "Coordinates validated successfully"

        except Exception as e:
            self.logger.error(f"Error validating coordinates: {e}")
            return False, f"Validation error: {str(e)}"

    def _is_within_sao_paulo_region(self, lat: float, lon: float) -> bool:
        """Check if coordinates are within São Paulo state bounds"""
        # São Paulo state approximate bounds
        SP_BOUNDS = {
            'lat_min': -25.5,
            'lat_max': -19.5,
            'lon_min': -53.5,
            'lon_max': -44.0
        }

        return (SP_BOUNDS['lat_min'] <= lat <= SP_BOUNDS['lat_max'] and
                SP_BOUNDS['lon_min'] <= lon <= SP_BOUNDS['lon_max'])

    def analyze_catchment_area(self,
                             center_lat: float,
                             center_lon: float,
                             radius_km: float,
                             municipality_data: pd.DataFrame,
                             analysis_columns: List[str] = None) -> Dict[str, Any]:
        """
        Comprehensive catchment area analysis

        Args:
            center_lat: Center latitude
            center_lon: Center longitude
            radius_km: Analysis radius in kilometers
            municipality_data: Municipality data DataFrame
            analysis_columns: Columns to analyze (defaults to biogas-related columns)

        Returns:
            Comprehensive analysis results dictionary
        """
        try:
            # Validate inputs
            is_valid, msg = self.validate_coordinates(center_lat, center_lon, radius_km)
            if not is_valid:
                return {'error': msg, 'center': (center_lat, center_lon), 'radius_km': radius_km}

            # Default analysis columns
            if analysis_columns is None:
                analysis_columns = [
                    'potencial_biogas_total',
                    'potencial_biogas_animais',
                    'potencial_biogas_agricola',
                    'populacao_total'
                ]

            # Find municipalities in radius
            municipalities_in_radius = self.geospatial_analyzer.find_municipalities_in_radius(
                municipality_data, center_lat, center_lon, radius_km
            )

            if municipalities_in_radius.empty:
                return {
                    'center': (center_lat, center_lon),
                    'radius_km': radius_km,
                    'municipalities_found': 0,
                    'message': 'No municipalities found within radius'
                }

            # Calculate comprehensive statistics
            results = {
                'center': (center_lat, center_lon),
                'radius_km': radius_km,
                'analysis_timestamp': pd.Timestamp.now().isoformat(),
                'municipalities_found': len(municipalities_in_radius),
                'geographic_info': self._calculate_geographic_info(center_lat, center_lon, radius_km),
                'municipality_statistics': {},
                'biogas_analysis': {},
                'optimization_metrics': {}
            }

            # Analyze each column
            for column in analysis_columns:
                if column in municipalities_in_radius.columns:
                    stats = self._calculate_column_statistics(
                        municipalities_in_radius, column, center_lat, center_lon, radius_km
                    )
                    results['municipality_statistics'][column] = stats

            # Specialized biogas analysis
            results['biogas_analysis'] = self._analyze_biogas_potential(municipalities_in_radius)

            # Calculate optimization metrics
            results['optimization_metrics'] = self._calculate_optimization_metrics(
                municipalities_in_radius, center_lat, center_lon
            )

            # Add municipality details
            results['municipality_details'] = self._format_municipality_details(municipalities_in_radius)

            self.logger.info(f"Catchment analysis completed: {len(municipalities_in_radius)} municipalities")
            return results

        except Exception as e:
            self.logger.error(f"Error in catchment area analysis: {e}")
            return {
                'error': f"Analysis failed: {str(e)}",
                'center': (center_lat, center_lon),
                'radius_km': radius_km
            }

    def _calculate_geographic_info(self, center_lat: float, center_lon: float, radius_km: float) -> Dict[str, Any]:
        """Calculate geographic information for the analysis area"""
        try:
            # Calculate area
            area_km2 = math.pi * radius_km ** 2

            # Estimate population density (approximate)
            # This is a rough estimate based on São Paulo state density
            estimated_density = 166  # people per km² (São Paulo state average)
            estimated_population = area_km2 * estimated_density

            return {
                'center_coordinates': {
                    'latitude': center_lat,
                    'longitude': center_lon,
                    'formatted': f"{center_lat:.4f}, {center_lon:.4f}"
                },
                'analysis_radius_km': radius_km,
                'total_area_km2': round(area_km2, 2),
                'total_area_ha': round(area_km2 * 100, 2),
                'estimated_population': round(estimated_population, 0),
                'region_type': self._determine_region_type(center_lat, center_lon)
            }

        except Exception as e:
            self.logger.error(f"Error calculating geographic info: {e}")
            return {}

    def _determine_region_type(self, lat: float, lon: float) -> str:
        """Determine region type based on coordinates"""
        # Simplified region classification for São Paulo
        if lat > -21:
            return "Norte (North)"
        elif lat < -23.5:
            return "Sul (South)"
        elif lon > -47:
            return "Leste (East)"
        elif lon < -49:
            return "Oeste (West)"
        else:
            return "Centro (Central)"

    def _calculate_column_statistics(self,
                                   df: pd.DataFrame,
                                   column: str,
                                   center_lat: float,
                                   center_lon: float,
                                   radius_km: float) -> Dict[str, Any]:
        """Calculate comprehensive statistics for a specific column"""
        try:
            # Filter valid data
            valid_data = df[column].dropna()

            if valid_data.empty:
                return {'error': f'No valid data for {column}'}

            # Basic statistics
            stats = {
                'total': float(valid_data.sum()),
                'mean': float(valid_data.mean()),
                'median': float(valid_data.median()),
                'std': float(valid_data.std()) if len(valid_data) > 1 else 0.0,
                'min': float(valid_data.min()),
                'max': float(valid_data.max()),
                'count': len(valid_data),
                'count_non_zero': len(valid_data[valid_data > 0])
            }

            # Percentiles
            stats['percentiles'] = {
                '25th': float(valid_data.quantile(0.25)),
                '75th': float(valid_data.quantile(0.75)),
                '90th': float(valid_data.quantile(0.90)),
                '95th': float(valid_data.quantile(0.95))
            }

            # Distribution analysis
            stats['distribution'] = {
                'zeros': len(valid_data[valid_data == 0]),
                'low_values': len(valid_data[(valid_data > 0) & (valid_data <= stats['percentiles']['25th'])]),
                'medium_values': len(valid_data[(valid_data > stats['percentiles']['25th']) &
                                              (valid_data <= stats['percentiles']['75th'])]),
                'high_values': len(valid_data[valid_data > stats['percentiles']['75th']])
            }

            # Distance-weighted analysis
            if 'distance_km' in df.columns:
                stats['distance_weighted'] = self._calculate_distance_weighted_stats(df, column)

            return stats

        except Exception as e:
            self.logger.error(f"Error calculating statistics for {column}: {e}")
            return {'error': f'Calculation failed for {column}'}

    def _calculate_distance_weighted_stats(self, df: pd.DataFrame, column: str) -> Dict[str, float]:
        """Calculate distance-weighted statistics"""
        try:
            valid_df = df[(df[column].notna()) & (df['distance_km'].notna())].copy()

            if valid_df.empty:
                return {}

            # Calculate weights (closer = higher weight)
            max_distance = valid_df['distance_km'].max()
            valid_df['weight'] = 1 - (valid_df['distance_km'] / max_distance)

            # Weighted statistics
            total_weight = valid_df['weight'].sum()

            if total_weight == 0:
                return {}

            weighted_mean = (valid_df[column] * valid_df['weight']).sum() / total_weight
            weighted_total = valid_df[column].sum()  # Not actually weighted for total

            return {
                'weighted_mean': float(weighted_mean),
                'total_within_radius': float(weighted_total),
                'effective_contributors': len(valid_df[valid_df[column] > 0])
            }

        except Exception as e:
            self.logger.error(f"Error calculating distance-weighted stats: {e}")
            return {}

    def _analyze_biogas_potential(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Specialized biogas potential analysis"""
        try:
            biogas_columns = [col for col in df.columns if 'biogas' in col.lower()]

            if not biogas_columns:
                return {'error': 'No biogas columns found'}

            analysis = {
                'total_potential_m3_year': {},
                'breakdown_by_source': {},
                'top_contributors': {},
                'feasibility_assessment': {}
            }

            # Analyze each biogas column
            for col in biogas_columns:
                valid_data = df[col].dropna()
                if not valid_data.empty:
                    analysis['total_potential_m3_year'][col] = float(valid_data.sum())

                    # Top contributors
                    top_municipalities = df.nlargest(5, col)[['nome_municipio', col]].to_dict('records')
                    analysis['top_contributors'][col] = top_municipalities

            # Overall assessment
            if 'potencial_biogas_total' in df.columns:
                total_potential = df['potencial_biogas_total'].sum()
                analysis['feasibility_assessment'] = self._assess_biogas_feasibility(total_potential, len(df))

            return analysis

        except Exception as e:
            self.logger.error(f"Error in biogas potential analysis: {e}")
            return {'error': f'Biogas analysis failed: {str(e)}'}

    def _assess_biogas_feasibility(self, total_potential: float, municipality_count: int) -> Dict[str, Any]:
        """Assess biogas project feasibility"""
        try:
            # Simplified feasibility thresholds (can be configured)
            FEASIBILITY_THRESHOLDS = {
                'very_high': 50000000,  # 50M m³/year
                'high': 20000000,       # 20M m³/year
                'medium': 5000000,      # 5M m³/year
                'low': 1000000,         # 1M m³/year
            }

            # Determine feasibility level
            if total_potential >= FEASIBILITY_THRESHOLDS['very_high']:
                level = 'Very High'
                description = 'Excellent potential for large-scale biogas plants'
            elif total_potential >= FEASIBILITY_THRESHOLDS['high']:
                level = 'High'
                description = 'Good potential for medium to large-scale projects'
            elif total_potential >= FEASIBILITY_THRESHOLDS['medium']:
                level = 'Medium'
                description = 'Suitable for small to medium-scale projects'
            elif total_potential >= FEASIBILITY_THRESHOLDS['low']:
                level = 'Low'
                description = 'Limited potential, consider distributed approach'
            else:
                level = 'Very Low'
                description = 'Insufficient potential for commercial projects'

            # Calculate density metrics
            average_per_municipality = total_potential / municipality_count if municipality_count > 0 else 0

            return {
                'feasibility_level': level,
                'description': description,
                'total_potential_m3_year': float(total_potential),
                'average_per_municipality': float(average_per_municipality),
                'municipality_count': municipality_count,
                'potential_plant_capacity_mw': self._estimate_plant_capacity(total_potential)
            }

        except Exception as e:
            self.logger.error(f"Error assessing feasibility: {e}")
            return {}

    def _estimate_plant_capacity(self, annual_m3: float) -> float:
        """Estimate biogas plant capacity in MW"""
        try:
            # Simplified conversion: 1 m³ biogas ≈ 6 kWh (approximate)
            # Annual kWh = annual_m3 * 6
            # MW capacity ≈ annual_kWh / (8760 hours * capacity_factor)
            # Assuming 80% capacity factor

            annual_kwh = annual_m3 * 6
            capacity_factor = 0.8
            hours_per_year = 8760

            estimated_mw = annual_kwh / (hours_per_year * capacity_factor * 1000)  # Convert to MW

            return round(estimated_mw, 2)

        except Exception:
            return 0.0

    def _calculate_optimization_metrics(self, df: pd.DataFrame, center_lat: float, center_lon: float) -> Dict[str, Any]:
        """Calculate metrics for plant location optimization"""
        try:
            if 'distance_km' not in df.columns:
                return {}

            metrics = {
                'transport_optimization': {},
                'supply_concentration': {},
                'accessibility': {}
            }

            # Transport cost optimization (simplified)
            if 'potencial_biogas_total' in df.columns:
                # Weight by potential and distance
                df_valid = df[df['potencial_biogas_total'] > 0].copy()

                if not df_valid.empty:
                    # Calculate transport efficiency score
                    # Higher potential closer to center = better score
                    df_valid['transport_score'] = df_valid['potencial_biogas_total'] / (df_valid['distance_km'] + 1)

                    metrics['transport_optimization'] = {
                        'average_transport_score': float(df_valid['transport_score'].mean()),
                        'total_weighted_potential': float((df_valid['potencial_biogas_total'] / df_valid['distance_km']).sum()),
                        'optimal_supply_municipalities': len(df_valid[df_valid['distance_km'] <= 25])  # Within 25km
                    }

            # Supply concentration analysis
            if len(df) > 0:
                # Calculate how concentrated the supply is
                radius_ranges = [(0, 10), (10, 25), (25, 50), (50, 100)]
                concentration = {}

                for min_dist, max_dist in radius_ranges:
                    in_range = df[(df['distance_km'] >= min_dist) & (df['distance_km'] < max_dist)]
                    concentration[f'{min_dist}-{max_dist}km'] = {
                        'municipality_count': len(in_range),
                        'total_potential': float(in_range.get('potencial_biogas_total', pd.Series([0])).sum())
                    }

                metrics['supply_concentration'] = concentration

            return metrics

        except Exception as e:
            self.logger.error(f"Error calculating optimization metrics: {e}")
            return {}

    def _format_municipality_details(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Format municipality details for display"""
        try:
            # Select relevant columns
            display_columns = ['nome_municipio', 'distance_km']

            # Add biogas columns if available
            biogas_columns = [col for col in df.columns if 'biogas' in col.lower()]
            display_columns.extend(biogas_columns[:3])  # Top 3 biogas columns

            # Add population if available
            if 'populacao_total' in df.columns:
                display_columns.append('populacao_total')

            # Filter existing columns
            available_columns = [col for col in display_columns if col in df.columns]

            # Sort by distance and get top municipalities
            df_sorted = df.sort_values('distance_km').head(20)  # Top 20 closest

            # Format for display
            municipality_list = []
            for _, row in df_sorted.iterrows():
                municipality = {}
                for col in available_columns:
                    if pd.notna(row[col]):
                        if col == 'distance_km':
                            municipality[col] = round(row[col], 2)
                        elif 'biogas' in col.lower():
                            municipality[col] = round(row[col], 0)
                        else:
                            municipality[col] = row[col]

                municipality_list.append(municipality)

            return municipality_list

        except Exception as e:
            self.logger.error(f"Error formatting municipality details: {e}")
            return []

    def find_optimal_locations(self,
                             municipality_data: pd.DataFrame,
                             search_area_bounds: Dict[str, float],
                             grid_resolution: float = 0.1) -> List[Dict[str, Any]]:
        """
        Find optimal biogas plant locations using grid search

        Args:
            municipality_data: Municipality data DataFrame
            search_area_bounds: Dictionary with lat_min, lat_max, lon_min, lon_max
            grid_resolution: Grid resolution in degrees

        Returns:
            List of optimal location candidates
        """
        try:
            if not HAS_GEOSPATIAL:
                return []

            self.logger.info("Starting optimal location search...")

            # Create search grid
            lat_points = np.arange(
                search_area_bounds['lat_min'],
                search_area_bounds['lat_max'],
                grid_resolution
            )
            lon_points = np.arange(
                search_area_bounds['lon_min'],
                search_area_bounds['lon_max'],
                grid_resolution
            )

            candidates = []
            analysis_radius = 30  # km

            # Evaluate each grid point
            for lat in lat_points:
                for lon in lon_points:
                    # Quick validation
                    if not self._is_within_sao_paulo_region(lat, lon):
                        continue

                    # Analyze this location
                    analysis = self.analyze_catchment_area(
                        lat, lon, analysis_radius, municipality_data,
                        ['potencial_biogas_total']
                    )

                    if 'error' not in analysis and analysis.get('municipalities_found', 0) > 0:
                        # Calculate optimization score
                        score = self._calculate_location_score(analysis)

                        if score > 0:
                            candidates.append({
                                'latitude': lat,
                                'longitude': lon,
                                'score': score,
                                'municipalities_count': analysis['municipalities_found'],
                                'total_potential': analysis.get('municipality_statistics', {}).get(
                                    'potencial_biogas_total', {}
                                ).get('total', 0),
                                'analysis': analysis
                            })

            # Sort by score and return top candidates
            candidates.sort(key=lambda x: x['score'], reverse=True)

            self.logger.info(f"Found {len(candidates)} location candidates")
            return candidates[:10]  # Top 10 candidates

        except Exception as e:
            self.logger.error(f"Error finding optimal locations: {e}")
            return []

    def _calculate_location_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate optimization score for a location"""
        try:
            score = 0.0

            # Biogas potential score (40% weight)
            biogas_stats = analysis.get('municipality_statistics', {}).get('potencial_biogas_total', {})
            total_potential = biogas_stats.get('total', 0)
            score += (total_potential / 1000000) * 0.4  # Normalize by 1M m³

            # Municipality count score (20% weight)
            municipality_count = analysis.get('municipalities_found', 0)
            score += min(municipality_count / 10, 1.0) * 0.2  # Normalize by 10 municipalities

            # Concentration score (20% weight)
            # Higher scores for more concentrated resources
            if municipality_count > 0:
                avg_potential = total_potential / municipality_count
                concentration_score = min(avg_potential / 500000, 1.0)  # Normalize by 500k m³
                score += concentration_score * 0.2

            # Transport optimization score (20% weight)
            optimization_metrics = analysis.get('optimization_metrics', {})
            transport_metrics = optimization_metrics.get('transport_optimization', {})
            transport_score = transport_metrics.get('average_transport_score', 0)
            normalized_transport = min(transport_score / 1000000, 1.0)  # Normalize
            score += normalized_transport * 0.2

            return round(score, 4)

        except Exception as e:
            self.logger.error(f"Error calculating location score: {e}")
            return 0.0


# Factory function
@st.cache_resource
def get_proximity_analyzer() -> ProximityAnalyzer:
    """
    Get cached ProximityAnalyzer instance

    Returns:
        ProximityAnalyzer instance
    """
    return ProximityAnalyzer()


# Convenience functions
def analyze_proximity(center_lat: float,
                     center_lon: float,
                     radius_km: float,
                     municipality_data: pd.DataFrame) -> Dict[str, Any]:
    """
    Convenience function for proximity analysis

    Args:
        center_lat: Center latitude
        center_lon: Center longitude
        radius_km: Analysis radius in kilometers
        municipality_data: Municipality data DataFrame

    Returns:
        Analysis results dictionary
    """
    analyzer = get_proximity_analyzer()
    return analyzer.analyze_catchment_area(center_lat, center_lon, radius_km, municipality_data)


def validate_analysis_coordinates(lat: float, lon: float, radius_km: float) -> Tuple[bool, str]:
    """
    Convenience function for coordinate validation

    Args:
        lat: Latitude
        lon: Longitude
        radius_km: Radius in kilometers

    Returns:
        Tuple of (is_valid, message)
    """
    analyzer = get_proximity_analyzer()
    return analyzer.validate_coordinates(lat, lon, radius_km)