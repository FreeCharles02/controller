class MotorControlWatcher: 
    def __init__(self):
        self.lf_value = 0.0
        self.lb_value = 0.0
        self.rf_value = 0.0
        self.rb_value = 0.0
        self.observer = False
    
    def notify(self, lf_new_value, lb_new_value, rf_new_value, rb_new_value):
          if lf_new_value != self.lf_value or lb_new_value != self.lb_value or rf_new_value != self.rf_value or rb_new_value != self.rb_value:
               self.observer = True
          else:
               self.observer = False
    
