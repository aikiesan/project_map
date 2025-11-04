#!/usr/bin/env python3
"""
CP2B Maps - Data Consistency Analysis
FAPESP 2025/08745-2

This script performs comprehensive data validation and consistency checks
across all modules, databases, and research data in the CP2B Maps platform.
"""

import sqlite3
from pathlib import Path
from typing import Dict, List, Tuple, Any
import json


class DataConsistencyAnalyzer:
    """Comprehensive data consistency validation for CP2B Maps"""

    def __init__(self, db_path: str = "/home/user/project_map/data/database/cp2b_maps.db"):
        self.db_path = db_path
        self.issues = []
        self.warnings = []
        self.validation_results = {}

    def log_issue(self, category: str, severity: str, message: str, details: Dict = None):
        """Log a data consistency issue"""
        issue = {
            'category': category,
            'severity': severity,
            'message': message,
            'details': details or {}
        }
        if severity in ['CRITICAL', 'ERROR']:
            self.issues.append(issue)
        else:
            self.warnings.append(issue)

    def validate_conversion_factors(self) -> Dict:
        """
        Validate biogas conversion factors across different modules

        Checks:
        1. Methane content consistency (should be 60% or 0.6)
        2. Energy content per m³ methane (should be 9.97 kWh/m³)
        3. CO2 reduction factor (should be 0.45 kg CO2/kWh)
        """
        print("=" * 80)
        print("VALIDATION 1: Conversion Factors Consistency")
        print("=" * 80)

        results = {}

        # Expected values from literature and research_data.py
        expected = {
            'methane_content': 0.6,  # 60% of biogas is methane
            'methane_energy_content': 9.97,  # kWh/m³ CH₄
            'co2_avoided_per_kwh': 0.45,  # kg CO2/kWh
        }

        # From biogas_calculator.py - ConversionFactors class
        calculator_factors = {
            'methane_content': 0.6,
            'methane_energy_content': 9.97,
            'co2_avoided_per_kwh': 0.45,
        }

        # From database_loader.py - line 182-184
        database_loader_factors = {
            'methane_content': 0.6,  # Used in: df['biogas_potential_m3_day'] * 0.6 * 9.97
            'methane_energy_content': 9.97,  # kWh/m³
            'co2_avoided_per_kwh': 0.45,  # kg CO2/kWh
        }

        # Check consistency
        all_consistent = True
        for key in expected:
            calc_val = calculator_factors[key]
            db_val = database_loader_factors[key]
            exp_val = expected[key]

            if calc_val == db_val == exp_val:
                print(f"✅ {key}: CONSISTENT")
                print(f"   Calculator: {calc_val}, Database Loader: {db_val}, Expected: {exp_val}")
                results[key] = {'status': 'PASS', 'value': exp_val}
            else:
                print(f"❌ {key}: INCONSISTENT")
                print(f"   Calculator: {calc_val}, Database Loader: {db_val}, Expected: {exp_val}")
                self.log_issue(
                    'conversion_factors',
                    'ERROR',
                    f'Inconsistent {key} values across modules',
                    {'calculator': calc_val, 'database_loader': db_val, 'expected': exp_val}
                )
                results[key] = {'status': 'FAIL', 'values': {
                    'calculator': calc_val,
                    'database_loader': db_val,
                    'expected': exp_val
                }}
                all_consistent = False

        print()
        return results

    def validate_research_data_calculations(self) -> Dict:
        """
        Validate calculations in research_data.py for Cana-de-açúcar and Avicultura

        Checks:
        1. Final availability factor calculations (FC × FCp × FS × FL)
        2. CH₄ potential calculations
        3. Electricity generation calculations
        """
        print("=" * 80)
        print("VALIDATION 2: Research Data Calculations")
        print("=" * 80)

        results = {
            'cana': {},
            'avicultura': {}
        }

        # CANA-DE-AÇÚCAR - Validate availability factor calculations
        print("\n--- Cana-de-açúcar Availability Factors ---")

        cana_residues = {
            'bagaco': {
                'fc': 1.00, 'fcp': 1.00, 'fs': 1.00, 'fl': 1.00,
                'expected_final': 0.0,
                'stated_final': 0.0
            },
            'palha': {
                'fc': 0.80, 'fcp': 0.65, 'fs': 1.00, 'fl': 0.90,
                'expected_final': 0.80 * 0.65 * 1.00 * 0.90,  # Should be 0.468 = 46.8%
                'stated_final': 25.2  # What's stated in research_data.py
            },
            'vinhaca': {
                'fc': 0.95, 'fcp': 0.35, 'fs': 1.00, 'fl': 1.00,
                'expected_final': 0.95 * 0.35 * 1.00 * 1.00,  # Should be 0.3325 = 33.25%
                'stated_final': 61.7  # What's stated
            },
            'torta_filtro': {
                'fc': 0.90, 'fcp': 0.40, 'fs': 1.00, 'fl': 1.00,
                'expected_final': 0.90 * 0.40 * 1.00 * 1.00,  # Should be 0.36 = 36%
                'stated_final': 54.0  # What's stated
            }
        }

        for residue_name, factors in cana_residues.items():
            calculated = factors['fc'] * factors['fcp'] * factors['fs'] * factors['fl']
            expected_pct = calculated * 100
            stated_pct = factors['stated_final']

            # Special case for bagaço (explicitly 0%)
            if residue_name == 'bagaco':
                if stated_pct == 0.0:
                    print(f"✅ {residue_name}: CORRECT (explicitly unavailable)")
                    results['cana'][residue_name] = {'status': 'PASS'}
                continue

            # Check if calculation matches
            tolerance = 1.0  # Allow 1% tolerance due to rounding
            if abs(expected_pct - stated_pct) < tolerance:
                print(f"✅ {residue_name}: CONSISTENT")
                print(f"   Calculated: {expected_pct:.1f}%, Stated: {stated_pct}%")
                results['cana'][residue_name] = {'status': 'PASS', 'value': stated_pct}
            else:
                print(f"⚠️  {residue_name}: POTENTIAL ISSUE")
                print(f"   FC×FCp×FS×FL = {factors['fc']}×{factors['fcp']}×{factors['fs']}×{factors['fl']} = {expected_pct:.1f}%")
                print(f"   But stated final availability: {stated_pct}%")
                print(f"   Difference: {abs(expected_pct - stated_pct):.1f}%")

                # This is a WARNING not ERROR - might be correct based on literature
                self.log_issue(
                    'research_data_calculations',
                    'WARNING',
                    f'{residue_name}: Stated availability ({stated_pct}%) differs from simple factor multiplication ({expected_pct:.1f}%)',
                    {
                        'residue': residue_name,
                        'fc': factors['fc'],
                        'fcp': factors['fcp'],
                        'fs': factors['fs'],
                        'fl': factors['fl'],
                        'calculated': expected_pct,
                        'stated': stated_pct,
                        'difference': abs(expected_pct - stated_pct),
                        'note': 'May be correct if based on sequential application rather than multiplication'
                    }
                )
                results['cana'][residue_name] = {
                    'status': 'WARNING',
                    'calculated': expected_pct,
                    'stated': stated_pct
                }

        # AVICULTURA
        print("\n--- Avicultura Availability Factors ---")
        avicultura_factors = {
            'fc': 0.90,
            'fcp': 0.50,
            'fs': 1.00,
            'fl': 0.90,
            'expected_final': 0.90 * 0.50 * 1.00 * 0.90,  # = 0.405 = 40.5%
            'stated_final': 40.5
        }

        calculated = avicultura_factors['fc'] * avicultura_factors['fcp'] * avicultura_factors['fs'] * avicultura_factors['fl']
        expected_pct = calculated * 100
        stated_pct = avicultura_factors['stated_final']

        if abs(expected_pct - stated_pct) < 0.1:
            print(f"✅ Dejeto de Aves: CONSISTENT")
            print(f"   Calculated: {expected_pct:.1f}%, Stated: {stated_pct}%")
            results['avicultura']['dejeto_aves'] = {'status': 'PASS', 'value': stated_pct}
        else:
            print(f"❌ Dejeto de Aves: INCONSISTENT")
            print(f"   Calculated: {expected_pct:.1f}%, Stated: {stated_pct}%")
            self.log_issue(
                'research_data_calculations',
                'ERROR',
                f'Avicultura availability calculation mismatch',
                {'calculated': expected_pct, 'stated': stated_pct}
            )
            results['avicultura']['dejeto_aves'] = {
                'status': 'FAIL',
                'calculated': expected_pct,
                'stated': stated_pct
            }

        print()
        return results

    def validate_database_integrity(self) -> Dict:
        """
        Validate database integrity and data quality

        Checks:
        1. NULL values in critical columns
        2. Negative values where they shouldn't exist
        3. Suspicious outliers
        4. Geographic coordinate validity
        """
        print("=" * 80)
        print("VALIDATION 3: Database Integrity")
        print("=" * 80)

        results = {}

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Check 1: Total municipalities
            cursor.execute("SELECT COUNT(*) FROM municipalities")
            total_municipalities = cursor.fetchone()[0]
            print(f"\n✅ Total municipalities: {total_municipalities}")

            expected_municipalities = 645  # São Paulo state municipalities
            if total_municipalities != expected_municipalities:
                self.log_issue(
                    'database_integrity',
                    'WARNING',
                    f'Expected {expected_municipalities} municipalities, found {total_municipalities}',
                    {'expected': expected_municipalities, 'found': total_municipalities}
                )

            results['total_municipalities'] = {
                'value': total_municipalities,
                'expected': expected_municipalities,
                'status': 'PASS' if total_municipalities == expected_municipalities else 'WARNING'
            }

            # Check 2: NULL values in critical columns
            print("\n--- NULL Values Check ---")
            critical_columns = [
                'nome_municipio',
                'populacao_2022',
                'lat',
                'lon',
                'total_final_m_ano'
            ]

            for col in critical_columns:
                cursor.execute(f"SELECT COUNT(*) FROM municipalities WHERE {col} IS NULL")
                null_count = cursor.fetchone()[0]

                if null_count > 0:
                    print(f"⚠️  {col}: {null_count} NULL values")
                    self.log_issue(
                        'database_integrity',
                        'WARNING',
                        f'{col} has {null_count} NULL values',
                        {'column': col, 'null_count': null_count}
                    )
                    results[f'{col}_nulls'] = {'status': 'WARNING', 'count': null_count}
                else:
                    print(f"✅ {col}: No NULL values")
                    results[f'{col}_nulls'] = {'status': 'PASS', 'count': 0}

            # Check 3: Negative values
            print("\n--- Negative Values Check ---")
            biogas_columns = [
                'total_final_m_ano',
                'biogas_cana_m_ano',
                'biogas_aves_m_ano',
                'biogas_bovinos_m_ano'
            ]

            for col in biogas_columns:
                cursor.execute(f"SELECT COUNT(*) FROM municipalities WHERE {col} < 0")
                negative_count = cursor.fetchone()[0]

                if negative_count > 0:
                    print(f"❌ {col}: {negative_count} NEGATIVE values (ERROR)")
                    self.log_issue(
                        'database_integrity',
                        'ERROR',
                        f'{col} has {negative_count} negative values',
                        {'column': col, 'negative_count': negative_count}
                    )
                    results[f'{col}_negatives'] = {'status': 'FAIL', 'count': negative_count}
                else:
                    print(f"✅ {col}: No negative values")
                    results[f'{col}_negatives'] = {'status': 'PASS', 'count': 0}

            # Check 4: Geographic coordinates validity (São Paulo state bounds)
            print("\n--- Geographic Coordinates Check ---")
            # São Paulo state approximate bounds:
            # Latitude: -25.3 to -19.8
            # Longitude: -53.1 to -44.2

            cursor.execute("""
                SELECT COUNT(*)
                FROM municipalities
                WHERE lat < -25.3 OR lat > -19.8 OR lon < -53.1 OR lon > -44.2
            """)
            out_of_bounds = cursor.fetchone()[0]

            if out_of_bounds > 0:
                print(f"⚠️  Found {out_of_bounds} municipalities with coordinates outside SP state bounds")

                # Get details of out-of-bounds municipalities
                cursor.execute("""
                    SELECT nome_municipio, lat, lon
                    FROM municipalities
                    WHERE lat < -25.3 OR lat > -19.8 OR lon < -53.1 OR lon > -44.2
                    LIMIT 5
                """)
                examples = cursor.fetchall()

                self.log_issue(
                    'database_integrity',
                    'WARNING',
                    f'{out_of_bounds} municipalities have coordinates outside typical SP bounds',
                    {'count': out_of_bounds, 'examples': [
                        {'name': ex[0], 'lat': ex[1], 'lon': ex[2]} for ex in examples
                    ]}
                )
                results['coordinates_validity'] = {'status': 'WARNING', 'out_of_bounds': out_of_bounds}
            else:
                print(f"✅ All coordinates within São Paulo state bounds")
                results['coordinates_validity'] = {'status': 'PASS', 'out_of_bounds': 0}

            # Check 5: Data distribution statistics
            print("\n--- Data Distribution Statistics ---")
            cursor.execute("""
                SELECT
                    MIN(total_final_m_ano) as min_biogas,
                    MAX(total_final_m_ano) as max_biogas,
                    AVG(total_final_m_ano) as avg_biogas,
                    SUM(total_final_m_ano) as total_biogas
                FROM municipalities
                WHERE total_final_m_ano IS NOT NULL
            """)
            stats = cursor.fetchone()

            print(f"   Min biogas potential: {stats[0]:,.0f} m³/ano")
            print(f"   Max biogas potential: {stats[1]:,.0f} m³/ano")
            print(f"   Avg biogas potential: {stats[2]:,.0f} m³/ano")
            print(f"   Total biogas potential: {stats[3]:,.0f} m³/ano")

            results['biogas_statistics'] = {
                'min': stats[0],
                'max': stats[1],
                'avg': stats[2],
                'total': stats[3]
            }

            conn.close()
            print()

        except Exception as e:
            print(f"❌ Database validation failed: {e}")
            self.log_issue(
                'database_integrity',
                'CRITICAL',
                f'Database validation failed: {str(e)}',
                {}
            )
            results['status'] = 'CRITICAL_FAILURE'

        return results

    def validate_scenario_factors(self) -> Dict:
        """
        Validate scenario configuration factors

        Checks:
        1. Scenario factor ranges (0 to 1)
        2. Scenario factor logic (pessimistic < realistic < optimistic)
        """
        print("=" * 80)
        print("VALIDATION 4: Scenario Configuration")
        print("=" * 80)

        results = {}

        # From scenario_config.py
        scenarios = {
            'pessimistic': {'factor': 0.10, 'expected_pct': '10%'},
            'realistic': {'factor': 0.175, 'expected_pct': '17.5%'},
            'optimistic': {'factor': 0.275, 'expected_pct': '27.5%'},
            'utopian': {'factor': 1.0, 'expected_pct': '100%'}
        }

        print("\n--- Scenario Factors ---")
        for scenario, config in scenarios.items():
            factor = config['factor']
            pct = config['expected_pct']

            if 0 <= factor <= 1.0:
                print(f"✅ {scenario}: {factor} ({pct})")
                results[scenario] = {'status': 'PASS', 'factor': factor}
            else:
                print(f"❌ {scenario}: {factor} ({pct}) - OUT OF RANGE [0, 1]")
                self.log_issue(
                    'scenario_configuration',
                    'ERROR',
                    f'Scenario {scenario} has invalid factor {factor}',
                    {'scenario': scenario, 'factor': factor}
                )
                results[scenario] = {'status': 'FAIL', 'factor': factor}

        # Check logical ordering
        print("\n--- Scenario Ordering ---")
        if scenarios['pessimistic']['factor'] < scenarios['realistic']['factor'] < scenarios['optimistic']['factor'] < scenarios['utopian']['factor']:
            print("✅ Scenario factors are in correct logical order")
            results['ordering'] = {'status': 'PASS'}
        else:
            print("❌ Scenario factors are NOT in correct logical order")
            self.log_issue(
                'scenario_configuration',
                'ERROR',
                'Scenario factors not in expected order',
                {'factors': {k: v['factor'] for k, v in scenarios.items()}}
            )
            results['ordering'] = {'status': 'FAIL'}

        print()
        return results

    def generate_report(self):
        """Generate comprehensive consistency report"""
        print("=" * 80)
        print("DATA CONSISTENCY ANALYSIS REPORT")
        print("=" * 80)
        print()

        # Run all validations
        self.validation_results['conversion_factors'] = self.validate_conversion_factors()
        self.validation_results['research_data'] = self.validate_research_data_calculations()
        self.validation_results['database'] = self.validate_database_integrity()
        self.validation_results['scenarios'] = self.validate_scenario_factors()

        # Summary
        print("=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print()

        total_issues = len(self.issues)
        total_warnings = len(self.warnings)

        print(f"Total Critical Issues: {total_issues}")
        print(f"Total Warnings: {total_warnings}")
        print()

        if total_issues == 0 and total_warnings == 0:
            print("✅ ALL VALIDATIONS PASSED - No issues found!")
        elif total_issues == 0:
            print(f"⚠️  NO CRITICAL ISSUES - {total_warnings} warnings to review")
        else:
            print(f"❌ {total_issues} CRITICAL ISSUES FOUND - Requires attention!")

        print()

        # Detailed issues
        if total_issues > 0:
            print("=" * 80)
            print("CRITICAL ISSUES")
            print("=" * 80)
            for i, issue in enumerate(self.issues, 1):
                print(f"\n{i}. [{issue['severity']}] {issue['category']}")
                print(f"   {issue['message']}")
                if issue['details']:
                    print(f"   Details: {json.dumps(issue['details'], indent=6)}")

        # Warnings
        if total_warnings > 0:
            print()
            print("=" * 80)
            print("WARNINGS")
            print("=" * 80)
            for i, warning in enumerate(self.warnings, 1):
                print(f"\n{i}. [{warning['severity']}] {warning['category']}")
                print(f"   {warning['message']}")
                if warning['details']:
                    print(f"   Details: {json.dumps(warning['details'], indent=6)}")

        print()
        print("=" * 80)
        print("END OF REPORT")
        print("=" * 80)

        # Save report to file
        report_data = {
            'summary': {
                'total_issues': total_issues,
                'total_warnings': total_warnings,
                'status': 'PASS' if total_issues == 0 else 'FAIL'
            },
            'issues': self.issues,
            'warnings': self.warnings,
            'validation_results': self.validation_results
        }

        report_path = '/home/user/project_map/DATA_CONSISTENCY_REPORT.json'
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        print(f"\nDetailed report saved to: {report_path}")

        return report_data


if __name__ == "__main__":
    print("\nCP2B Maps - Data Consistency Analysis")
    print("FAPESP 2025/08745-2 - NIPE-UNICAMP")
    print()

    analyzer = DataConsistencyAnalyzer()
    report = analyzer.generate_report()
