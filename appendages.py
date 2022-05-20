import math
import pymunk
from pymunk.vec2d import Vec2d
from dataclasses import dataclass


class Organ():
    def hex_to_bin(self) -> None:
        scale = 16  ## equals to hexadecimal
        n_bits = 4
        self.gene_bin = bin(int(self.gene, scale))[2:].zfill(len(self.gene) * n_bits)

    def normalize(self, char) -> float:
        return (int(char, 2) / 2 ** len(char))

    def scale(self, norm_value, MAX, MIN) -> float:
        return max(MIN, norm_value * MAX)


@dataclass
class Head(Organ):
    id: str

    def __post_init__(self) -> None:
        self.HEAD_POSITION = (256, 256)
        self.DENSITY = 3
        self.HEAD_RADIUS = 12

        self.create()
            
    def create(self) -> None:
        self.matter = pymunk.Body()
        self.matter.position = self.HEAD_POSITION

        self.shape = pymunk.Circle(self.matter, self.HEAD_RADIUS)
        self.shape.density = self.DENSITY
        self.shape.color = (0, 0, 0, 100)


@dataclass
class Limb(Organ):
    gene: str
    id: str 

    def __post_init__(self):
        self.MAX_LENGTH = 24
        self.MIN_LENGTH = 4
        self.MAX_RADIUS = 5
        self.MIN_RADIUS = 2
        self.DENSITY = 1.2
        self.FRICTION = 0.5

        self.MAX_MOTOR_FORCE = 70000
        self.MIN_MOTOR_FORCE = 40000
        self.MAX_SPRING_STIFFNESS = 1.2
        self.MIN_SPRING_STIFFNESS = 0.8
        self.MAX_SPRING_DAMPING = 1.3
        self.MIN_SPRING_DAMPING = 0.7


        self.hex_to_bin()
        self.decode_gene()
        self.create()

    def decode_gene(self) -> None:
        v_x = self.gene_bin[:4]
        v_y = self.gene_bin[4:8]
        radius = self.gene_bin[8:10]
        flip_x = int(self.gene_bin[10])
        flip_y = int(self.gene_bin[11])
        self.side = int(self.gene_bin[12]) # left = 0, right = 1
        
        v_x = self.scale(
            self.normalize(v_x), 
            self.MAX_LENGTH,
            self.MIN_LENGTH
        )
        v_y = self.scale(
            self.normalize(v_y),
            self.MAX_LENGTH,
            self.MIN_LENGTH
        )

        if flip_x:
            v_x = -v_x
        if flip_y:
            v_y = -v_y

        self.v = Vec2d(v_x, v_y)
        
        self.radius = self.scale(
            self.normalize(radius),
            self.MAX_RADIUS,
            self.MIN_RADIUS
        )
       
        # we nee to do this as a consequence of pymunks quirky
        # center of gravity calcs when creating segments
        # see: http://www.pymunk.org/en/latest/overview.html#center-of-gravity 
        self.end_1 = (-v_x/2, -v_y/2)
        self.end_2 = (v_x/2, v_y/2)
        

        self.joint_mechanics = int(self.gene_bin[13:15], 2)
        
        self.motor_direction = int(self.gene_bin[15])
        self.motor_force = self.gene_bin[16:19]
        self.spring_stiffness = self.gene_bin[19:22]
        self.spring_damping = self.gene_bin[22:24]

        print(f"{self.motor_force=}")
        self.motor_force = self.scale(
            self.normalize(self.motor_force),
            self.MAX_MOTOR_FORCE,
            self.MIN_MOTOR_FORCE
        )

        self.spring_stiffness = self.scale(
            self.normalize(self.spring_stiffness),
            self.MAX_SPRING_STIFFNESS,
            self.MIN_SPRING_STIFFNESS
        )

        self.spring_stiffness = self.spring_stiffness * self.motor_force 

        self.spring_damping = self.scale(
            self.normalize(self.spring_damping),
            self.MAX_SPRING_DAMPING,
            self.MIN_SPRING_DAMPING
        )       

        
    def create(self) -> None:
        self.matter = pymunk.Body()
        # DONT INIT POSITION YET -> IT DEPENDS ON THE PARENT POS
            
        self.shape = pymunk.Segment(
            self.matter,
            self.end_1,
            self.end_2,
            self.radius
        )

        self.shape.density = self.DENSITY
        self.shape.friction = self.FRICTION
        self.shape.elasticity = 0
        self.shape.color = (0,0,0,100)



