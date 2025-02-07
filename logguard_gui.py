import customtkinter as ctk
from tkinter import messagebox
import re
import json
from main import main
class UserInfoApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("User Information")
        self.root.geometry("400x500")

        self.create_user_info_page()

    def create_user_info_page(self):
        # Create User Info page layout
        self.user_info_frame = ctk.CTkFrame(self.root)
        self.user_info_frame.pack(fill="both", expand=True)

        # Title
        title_label = ctk.CTkLabel(self.user_info_frame, text="User Information Form", font=("Helvetica", 16, "bold"))
        title_label.pack(pady=10)

        # Create form fields
        self.username_entry = self.create_form_field(self.user_info_frame, "User Name")
        self.email_entry = self.create_form_field(self.user_info_frame, "Email")

        # Working hours section
        hours_frame = ctk.CTkFrame(self.user_info_frame)
        hours_frame.pack(pady=10, fill="x")

        hours_label = ctk.CTkLabel(hours_frame, text="Working Hours", font=("Helvetica", 12, "bold"))
        hours_label.pack(pady=5)

        # Time selection frames
        start_frame = self.create_time_frame(hours_frame, "Start Time")
        self.start_hour, self.start_minute = self.start_time_vars = self.create_time_selectors(start_frame)

        end_frame = self.create_time_frame(hours_frame, "End Time")
        self.end_hour, self.end_minute = self.end_time_vars = self.create_time_selectors(end_frame)

        # Submit button
        submit_button = ctk.CTkButton(self.user_info_frame, text="Submit", command=self.validate_and_submit)
        submit_button.pack(pady=20)

    def create_dashboard_and_settings(self, username, email, start_hour, start_minute, end_hour, end_minute):
        # Destroy the current window
        self.root.destroy()

        # Create a new window
        self.tabview_window = ctk.CTk()
        self.tabview_window.title("Dashboard and Settings")
        self.tabview_window.geometry("400x500")

        # Store user data
        self.user_data = {
            "username": username,
            "email": email,
            "working_hours": {
                "start_hour": start_hour,
                "start_minute": start_minute,
                "end_hour": end_hour,
                "end_minute": end_minute
            },
            "days_back": 7  # Default value
        }

        # Create tab view
        self.tabview = ctk.CTkTabview(self.tabview_window)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        # Add tabs
        self.dashboard_tab = self.tabview.add("Dashboard")
        self.settings_tab = self.tabview.add("Settings")

        # Create dashboard content
        self.create_dashboard_tab()

        # Create settings content
        self.create_settings_tab()

        # Start the new window's event loop
        self.tabview_window.mainloop()

    def save_days_back_to_json(self):
        """Retrieve the value from the entry field and update both the UI and JSON."""
        if hasattr(self.days_back, 'get'):
            days_back_value = self.days_back.get().strip()
            if days_back_value.isdigit():
                days_back = int(days_back_value)
                self.user_data["days_back"] = days_back

                # Save to JSON
                with open("config.json", "w") as file:
                    json.dump(self.user_data, file, indent=4)

                messagebox.showinfo("Success", f"Days back set to {days_back}")
            else:
                messagebox.showerror("Error", "Please enter a valid number")

    def create_dashboard_tab(self):
        # Dashboard Tab content
        welcome_label = ctk.CTkLabel(
            self.dashboard_tab,
            text=f"Welcome, {self.user_data['username']}!",
            font=("Helvetica", 16, "bold")
        )
        welcome_label.pack(pady=20)
        self.days_back = self.create_form_field(self.dashboard_tab, "Days Back")
        set_button = ctk.CTkButton(self.dashboard_tab, text="Set", command=self.save_days_back_to_json)
        set_button.pack(pady=5)
        generate_summary_button = ctk.CTkButton(self.dashboard_tab, text="Generate Summary",
                                                command=main)
        generate_summary_button.pack(pady=10)

        # User info display
        info_frame = ctk.CTkFrame(self.dashboard_tab)
        info_frame.pack(pady=10, padx=10, fill="x")

        for key, value in self.user_data.items():
            label = ctk.CTkLabel(
                info_frame,
                text=f"{key.replace('_', ' ').title()}: {value}",
                anchor="w"
            )
            label.pack(fill="x", pady=5)

    # def generate_summary(self):
    #     """Trigger the login monitor with the specified days back"""
    #     try:
    #         days_back = int(self.days_back.get().strip())
    #         from main import run_login_monitor  # Import here to avoid circular imports
    #
    #         result = run_login_monitor(days_back)
    #         if result:
    #             messagebox.showinfo("Success", "Login summary generated successfully!")
    #         else:
    #             messagebox.showerror("Error", "Failed to generate login summary")
    #     except ValueError:
    #         messagebox.showerror("Error", "Please enter a valid number of days")
    #     except Exception as e:
    #         messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def create_settings_tab(self):
        # Settings Tab content
        # Email input field
        email_label = ctk.CTkLabel(self.settings_tab, text="Email:")
        email_label.pack(pady=10)

        self.settings_email_entry = ctk.CTkEntry(self.settings_tab)
        self.settings_email_entry.insert(0, self.user_data["email"])
        self.settings_email_entry.pack(pady=5)

        # Working hours section
        working_hours_label = ctk.CTkLabel(self.settings_tab, text="Working Hours:")
        working_hours_label.pack(pady=10)

        working_hours = self.user_data.get("working_hours", {})
        start_hour = working_hours.get("start_hour", "00")
        start_minute = working_hours.get("start_minute", "00")
        end_hour = working_hours.get("end_hour", "00")
        end_minute = working_hours.get("end_minute", "00")

        # Hour drop-down fields
        hours = [str(i).zfill(2) for i in range(24)]
        minutes = [str(i).zfill(2) for i in range(0, 60, 5)]

        # Start Hour
        start_hour_label = ctk.CTkLabel(self.settings_tab, text="Start Hour:")
        start_hour_label.pack(pady=5)
        self.start_hour_var = ctk.StringVar(value=start_hour)
        self.start_hour_menu = ctk.CTkOptionMenu(
            self.settings_tab,
            variable=self.start_hour_var,
            values=hours
        )
        self.start_hour_menu.pack(pady=5)

        # Start Minute
        start_minute_label = ctk.CTkLabel(self.settings_tab, text="Start Minute:")
        start_minute_label.pack(pady=5)
        self.start_minute_var = ctk.StringVar(value=start_minute)
        self.start_minute_menu = ctk.CTkOptionMenu(
            self.settings_tab,
            variable=self.start_minute_var,
            values=minutes
        )
        self.start_minute_menu.pack(pady=5)

        # End Hour
        end_hour_label = ctk.CTkLabel(self.settings_tab, text="End Hour:")
        end_hour_label.pack(pady=5)
        self.end_hour_var = ctk.StringVar(value=end_hour)
        self.end_hour_menu = ctk.CTkOptionMenu(
            self.settings_tab,
            variable=self.end_hour_var,
            values=hours
        )
        self.end_hour_menu.pack(pady=5)

        # End Minute
        end_minute_label = ctk.CTkLabel(self.settings_tab, text="End Minute:")
        end_minute_label.pack(pady=5)
        self.end_minute_var = ctk.StringVar(value=end_minute)
        self.end_minute_menu = ctk.CTkOptionMenu(
            self.settings_tab,
            variable=self.end_minute_var,
            values=minutes
        )
        self.end_minute_menu.pack(pady=5)

        # Save button
        save_button = ctk.CTkButton(self.settings_tab, text="Save", command=self.save_settings)
        save_button.pack(pady=20)

    def create_form_field(self, parent, label_text):
        container = ctk.CTkFrame(parent)
        container.pack(pady=5, fill="x")

        label = ctk.CTkLabel(container, text=label_text)
        label.pack(side="left", padx=10)

        entry = ctk.CTkEntry(container)
        entry.pack(side="right", padx=10, fill="x", expand=True)

        return entry

    def create_time_frame(self, parent, label_text):
        frame = ctk.CTkFrame(parent)
        frame.pack(pady=5, fill="x")

        label = ctk.CTkLabel(frame, text=label_text)
        label.pack(pady=2)

        return frame

    def create_time_selectors(self, parent):
        time_frame = ctk.CTkFrame(parent)
        time_frame.pack(fill="x")

        hour_var = ctk.CTkComboBox(time_frame, values=[f"{i:02d}" for i in range(24)])
        hour_var.pack(side="left", padx=5)

        minute_var = ctk.CTkComboBox(time_frame, values=[f"{i:02d}" for i in range(60)])
        minute_var.pack(side="left", padx=5)

        return hour_var, minute_var

    def validate_email(self, email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def validate_and_submit(self):
        # Get all values
        username = self.username_entry.get().strip()
        email = self.email_entry.get().strip()
        start_time = (self.start_hour.get(), self.start_minute.get())
        end_time = (self.end_hour.get(), self.end_minute.get())

        # Validation
        if not username:
            messagebox.showerror("Error", "Username is required")
            return

        if not email or not self.validate_email(email):
            messagebox.showerror("Error", "Please enter a valid email address")
            return

        # Convert times to compare them
        start_minutes = int(start_time[0]) * 60 + int(start_time[1])
        end_minutes = int(end_time[0]) * 60 + int(end_time[1])

        if start_minutes >= end_minutes:
            messagebox.showerror("Error", "End time must be after start time")
            return
        user_data = {
            "username": username,
            "email": email,
            "working_hours": {
                "start_hour": start_time[0],  # Use the tuple's values
                "start_minute": start_time[1],
                "end_hour": end_time[0],
                "end_minute": end_time[1]
            }
        }

        with open("config.json", "w") as file:
            json.dump(user_data, file, indent=4)

        print("User data saved:", user_data)

        # Create dashboard and settings window
        self.create_dashboard_and_settings(username, email, *start_time, *end_time)

    def save_settings(self):
        # Get updated email and working hours from settings tab
        new_email = self.settings_email_entry.get()
        start_hour = self.start_hour_var.get()
        start_minute = self.start_minute_var.get()
        end_hour = self.end_hour_var.get()
        end_minute = self.end_minute_var.get()

        # Validate and update settings
        if not self.validate_email(new_email):
            messagebox.showerror("Error", "Please enter a valid email address")
            return

        # Update user data
        self.user_data["email"] = new_email
        self.user_data["working_hours"] = f"{start_hour}:{start_minute} - {end_hour}:{end_minute}"

        # Clear existing dashboard content
        for widget in self.dashboard_tab.winfo_children():
            widget.destroy()

        # Recreate dashboard content with updated information
        welcome_label = ctk.CTkLabel(
            self.dashboard_tab,
            text=f"Welcome, {self.user_data['username']}!",
            font=("Helvetica", 16, "bold")
        )
        welcome_label.pack(pady=20)

        # User info display
        info_frame = ctk.CTkFrame(self.dashboard_tab)
        info_frame.pack(pady=10, padx=10, fill="x")

        for key, value in self.user_data.items():
            label = ctk.CTkLabel(
                info_frame,
                text=f"{key.replace('_', ' ').title()}: {value}",
                anchor="w"
            )
            label.pack(fill="x", pady=5)

        # Confirmation message
        messagebox.showinfo("Success", "Settings updated successfully!")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = UserInfoApp()
    app.run()