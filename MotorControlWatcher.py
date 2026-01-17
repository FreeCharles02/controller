class MotorControlWatcher: 
    def __init__(self):
        self.lf_value = 0.0
        self.lb_value = 0.0
        self.rf_value = 0.0
        self.rb_value = 0.0
        self.observer = False
    
    def notify(self, lf_new_value, lb_new_value, rf_new_value, rb_new_value):
        # Set observer to True when any motor value changes, and update stored values
        if (lf_new_value != self.lf_value or
            lb_new_value != self.lb_value or
            rf_new_value != self.rf_value or
            rb_new_value != self.rb_value):
            self.observer = True
        else:
            self.observer = False

        # Always update stored values so future comparisons reflect the latest state
        self.lf_value = lf_new_value
        self.lb_value = lb_new_value
        self.rf_value = rf_new_value
        self.rb_value = rb_new_value
    
