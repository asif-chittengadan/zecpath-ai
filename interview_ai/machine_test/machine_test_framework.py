class MachineTestFramework:
    TASK_TYPES = {
        "coding",
        "debugging",
        "file_based",
        "system_design",
    }

    def create_task(
        self,
        task_id,
        title,
        task_type,
        description,
        time_limit_minutes,
        input_data=None,
        expected_output=None,
    ):
        if not isinstance(task_id, str) or not task_id.strip():
            raise ValueError("task_id must be a non-empty string")

        if not isinstance(title, str) or not title.strip():
            raise ValueError("title must be a non-empty string")

        if task_type not in self.TASK_TYPES:
            raise ValueError("Unsupported task type")

        if not isinstance(description, str) or not description.strip():
            raise ValueError("description must be a non-empty string")

        if (
            not isinstance(time_limit_minutes, int)
            or isinstance(time_limit_minutes, bool)
            or time_limit_minutes <= 0
        ):
            raise ValueError("time_limit_minutes must be a positive integer")

        return {
            "task_id": task_id.strip(),
            "title": title.strip(),
            "task_type": task_type,
            "description": description.strip(),
            "time_limit_minutes": time_limit_minutes,
            "input_data": input_data,
            "expected_output": expected_output,
        }

    def validate_task(self, task):
        if not isinstance(task, dict):
            raise TypeError("task must be a dictionary")

        required = {
            "task_id",
            "title",
            "task_type",
            "description",
            "time_limit_minutes",
        }

        missing = required - task.keys()

        if missing:
            raise ValueError(
                f"Missing task fields: {sorted(missing)}"
            )

        if task["task_type"] not in self.TASK_TYPES:
            raise ValueError("Unsupported task type")

        if (
            not isinstance(task["time_limit_minutes"], int)
            or isinstance(task["time_limit_minutes"], bool)
            or task["time_limit_minutes"] <= 0
        ):
            raise ValueError("Invalid time limit")

        return True

    def get_supported_task_types(self):
        return sorted(self.TASK_TYPES)