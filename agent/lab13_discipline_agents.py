
import json
import os
from datetime import datetime


class MechanicalEngineeringAgent:
    """ME domain-specific worklet."""

    def run(self):
        print("\n[ME Agent] Analyzing Mechanical Engineering task...")

        mass = 10          # kg
        acceleration = 5   # m/s^2
        force = mass * acceleration

        result = {
            "domain": "Mechanical Engineering",
            "agent": "ME Agent",
            "task": "Calculate force using Newton's Second Law",
            "inputs": {
                "mass_kg": mass,
                "acceleration_m_s2": acceleration
            },
            "result": {
                "force_newtons": force
            },
            "status": "SUCCESS"
        }

        print(f"[ME Agent] Calculated Force: {force} N")
        return result


class CivilEngineeringAgent:
    """CE domain-specific worklet."""

    def run(self):
        print("\n[CE Agent] Analyzing Civil Engineering task...")

        length = 10
        width = 5
        depth = 0.2

        volume = length * width * depth

        result = {
            "domain": "Civil Engineering",
            "agent": "CE Agent",
            "task": "Calculate concrete volume",
            "inputs": {
                "length_m": length,
                "width_m": width,
                "depth_m": depth
            },
            "result": {
                "concrete_volume_m3": round(volume, 2)
            },
            "status": "SUCCESS"
        }

        print(f"[CE Agent] Calculated Concrete Volume: {volume} m3")
        return result


class ElectricalEngineeringAgent:
    """EE domain-specific worklet."""

    def run(self):
        print("\n[EE Agent] Analyzing Electrical Engineering task...")

        voltage = 12
        resistance = 4

        current = voltage / resistance
        power = voltage * current

        result = {
            "domain": "Electrical Engineering",
            "agent": "EE Agent",
            "task": "Calculate current and power using Ohm's Law",
            "inputs": {
                "voltage_volts": voltage,
                "resistance_ohms": resistance
            },
            "result": {
                "current_amperes": round(current, 2),
                "power_watts": round(power, 2)
            },
            "status": "SUCCESS"
        }

        print(f"[EE Agent] Calculated Current: {current} A")
        print(f"[EE Agent] Calculated Power: {power} W")
        return result


class DisciplineCoordinator:
    """Coordinates all discipline-specific worklets."""

    def __init__(self):
        self.output_dir = "output/lab13_discipline_agents"
        os.makedirs(self.output_dir, exist_ok=True)

        self.agents = [
            MechanicalEngineeringAgent(),
            CivilEngineeringAgent(),
            ElectricalEngineeringAgent()
        ]

        self.audit_log = []

    def run_all(self):
        print("\n" + "=" * 65)
        print("  LAB 13: DISCIPLINE-SPECIFIC AGENTS")
        print("  ME | CE | EE Domain Worklets")
        print("=" * 65)

        reports = []

        for agent in self.agents:
            report = agent.run()
            reports.append(report)

            self.audit_log.append({
                "agent": report["agent"],
                "domain": report["domain"],
                "status": report["status"],
                "timestamp": datetime.now().isoformat()
            })

        # Save individual and combined reports
        for report in reports:
            filename = report["agent"].lower().replace(" ", "_") + ".json"
            self.save_json(filename, report)

        self.save_json("combined_domain_report.json", reports)
        self.save_json("audit_log.json", self.audit_log)

        print("\n" + "=" * 65)
        print("  LAB 13 EXECUTION COMPLETED")
        print(f"  Agents Executed: {len(reports)}")
        print(f"  Successful: {sum(r['status'] == 'SUCCESS' for r in reports)}")
        print(f"  Output Directory: {os.path.abspath(self.output_dir)}")
        print("=" * 65)

    def save_json(self, filename, data):
        path = os.path.join(self.output_dir, filename)

        with open(path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

        print(f"[Saved] {path}")


if __name__ == "__main__":
    coordinator = DisciplineCoordinator()
    coordinator.run_all()
