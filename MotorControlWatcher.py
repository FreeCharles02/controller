class MotorControlWatcher: 
    def _init_(self):
        self.lf_value = None
        self.lb_value = None
        self.rf_value = None
        self.rb_value = None

        self.observers = []

    def set_lf_value(self, new_value):
        self.lf_value =  new_value
        self.notify()

    def set_lb_value(self, new_value):
        self.lb_value = new_value
        self.notify()
    
    def set_rf_value(self, new_value): 
        self.rf_value = new_value
        self.notify()
    
    def set_rb_value(self, new_value):
        self.rb_value = new_value
        self.notify()   
    
    def add_observer(self, observer):
        self.observers.append(observer)
    
    def notify(self):
        for observer in self.observers: 
            observer = True
            observer = False