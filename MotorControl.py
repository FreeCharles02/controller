class MotorControlWatcher: 
    def _init_(self):
        self._value = None
        self.observers = []

    def set_value(self, new_value):
        self._value =  new_value
        self.notify(new_value)
    
    def add_observer(self, observer):
        self.observers.append(observer)
    
    def notify(self, new_value):
        for observer in self.observers: 
            observer(new_value)