#Field Object class, for new comers: a class the definition of an object and it's properties
class FieldObject: 
    #Constructor accepts distance from sensor and the name of the bounding box overlayed over the object detected in the 
   # image and creates a new FieldObject to be tracked in autonomous
    def __init__(self, distance_sense, box_name):
       self.distance = distance_sense
       self.name = box_name

    #We capture and set the changing disance as the distance decreaes or increases. 
    def set_distance(self,distance_sense):
        self.distance = distance_sense