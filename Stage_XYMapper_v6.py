from __future__ import annotations
import tkinter as tk
from pylablib.devices import Thorlabs
from copy import deepcopy
from tkinter import messagebox
import threading
from abc import ABC, abstractmethod
import time


###/////////////////////////////-Main-Code-///////////////////////////////////////////

# Stage is the base abstract class for both ThorlabsStage and VirtualStage classes.
# Stages can move, get id, get current position and update/create their UI.
class Stage(ABC):
    @abstractmethod
    def __init__(self, id: str, col: int, frame: tk.Frame, state: str):
        self.id = id
        self.col = col
        self.frame = frame
        self.state = state
        
    @abstractmethod
    def move(self):
        pass
    
    @abstractmethod
    def move_from_input(self):
        pass
    
    @abstractmethod
    def update_position_labels(self):
        pass
    
    @property
    @abstractmethod
    def id_get(self):
        pass

    @abstractmethod
    def stage_close(self):
        pass

    @abstractmethod
    def create_ui(self):
        pass

    @property
    @abstractmethod
    def get_position(self):
        pass


# ThorlabsStage class is handling the communication with Thorlabs KDC101 controller through pylablib.Thorlabs.
# The real stage object is self.motor.

class ThorlabsStage(Stage):
    def __init__(self, id: str, col: int, frame: tk.Frame, state: str):
        super().__init__(id,col,frame,state)
        self.motor = Thorlabs.KinesisMotor(self.id, scale= "stage")
        self.read_init_file()
        self.units = self.motor.get_scale_units()
        self.create_ui()
        if self.units == "m":
            self.convert = 1 / 1000
            self.units = "mm"
        else:
            self.convert = 1
        self.stg_home()
        print(self.motor.get_velocity_parameters())


    def move(self, end, check: bool, update_now: bool):
        if check == True:
            try:
                end = float(end) * self.convert
            except:
                new_end = ""
                for symbol in end:
                    if symbol == ",":
                        new_end += "."
                    elif symbol.isalpha():
                        return "It is not a number, did not move the stage."
                    elif symbol != " ":
                        new_end += symbol

                    end = float(new_end) * self.convert
        else:
            end = float(end) * self.convert
        
        self.motor.move_to(end)
        if update_now == True:
            self.motor.wait_for_stop()
            self.update_position_labels()
        try:
            if self.frame.mapper_window.state() == 'normal':
                self.frame.mapper.update_canvas_marker()
                self.frame.mapper.update_position_labels()
        except:
            pass
    

    def move_from_input(self):
        endpoint = self.inputText.get(1.0, "end-1c")
        self.move(endpoint,check=True,update_now=True)


    def update_position_labels(self):
        self.posLabel.config(text=f"Current position: {round(self.get_position / self.convert, 3)} {self.units}")

    @property
    def id_get(self):
        return self.id


    def stage_close(self):
        self.motor.close()


    def stg_home(self):
        self.motor.home()
        self.motor.wait_for_home()
        self.update_position_labels()


    def create_ui(self):
        self.stage_header = tk.Label(self.frame, text=f"Stage {self.id}", state=self.state)
        self.stage_header.grid(column=self.col, row=0, padx=10, pady=10)
        
        self.identify_button = tk.Button(self.frame, text="Identify me",command=self.motor.blink)
        self.identify_button.grid(column=self.col, row=1, padx=10, pady=10)

        self.inputText = tk.Text(self.frame, height=1, width=10, state=self.state)
        self.inputText.grid(column=self.col, row=2, padx=10, pady=10)

        self.moveButton = tk.Button(self.frame, text="Go!", command=self.move_from_input, state=self.state, height=2, width=10)
        self.moveButton.grid(column=self.col, row=3, padx=10, pady=10)

        self.posLabel = tk.Label(self.frame, text=f"")
        self.posLabel.config(text=f"Current position: {round(self.get_position, 3)} {self.units}")
        self.posLabel.grid(column=self.col, row=5, padx=10, pady=10)


    def read_init_file(self):
        init_file = open("stages_init_file.ini","r")
        lines = init_file.readlines()
        acc = float(lines[0].split(" ")[1])
        velocity = float(lines[1].split(" ")[1])
        init_file.close()

        self.motor.setup_velocity(min_velocity=0.0,acceleration=acc, max_velocity=velocity)

    def wait_for_stop(self):
        self.motor.wait_for_stop()
    
    @property
    def get_position(self):
        return self.motor.get_position()



# For the purpose of testing, the program can handle virtual stages. You can add them using a button "add virtual stage".
# Instead of having a real position like Thorlabs stage, virtual stage has a variable self.position.
# For increased realness, a delay is added to a move of a virtual stage, to simulate real movement.
class VirtualStage(Stage):
    def __init__(self, id: str, col: int, frame: tk.Frame, state: str):
        super().__init__(id,col,frame,state)
        self.position = 0
        self.create_ui()

    
    def move(self,end,check,update_now):
        if check == True:
            try:
                end = float(end)
            except:
                new_end = ""
                for symbol in end:
                    if symbol == ",":
                        new_end += "."
                    elif symbol.isalpha():
                        return "It is not a number, did not move the stage."
                    elif symbol != " ":
                        new_end += symbol

                    end = float(new_end)
        else:
            end = float(end)
        self.position = end

        if update_now == True:
            self.update_position_labels()
        try:
            if self.frame.mapper_window.state() == 'normal':
                self.frame.mapper.update_canvas_marker()
                self.frame.mapper.update_position_labels()
        except:
            pass

        time.sleep(0.2)
    
    
    def move_from_input(self):
        endpoint = self.inputText.get(1.0, "end-1c")
        self.move(endpoint,check=True,update_now=True)
    
    
    def update_position_labels(self):
        self.posLabel.config(text=f"Current position: {self.get_position} mm")

    @property
    def id_get(self):
        return self.id

    @property
    def get_position(self):
        return self.position
    
    def stage_close(self):
        pass

    
    def create_ui(self):
        self.stage_header = tk.Label(self.frame, text=f"Virtual Stage {self.id}", state=self.state)
        self.stage_header.grid(column=self.col, row=0, padx=10, pady=10)
        
        self.identify_button = tk.Button(self.frame, text="Identify me",command=self.blink)
        self.identify_button.grid(column=self.col, row=1, padx=10, pady=10)

        self.inputText = tk.Text(self.frame, height=1, width=10, state=self.state)
        self.inputText.grid(column=self.col, row=2, padx=10, pady=10)

        self.moveButton = tk.Button(self.frame, text="Go!", command=self.move_from_input, state=self.state, height=2, width=10)
        self.moveButton.grid(column=self.col, row=3, padx=10, pady=10)

        self.posLabel = tk.Label(self.frame, text="")
        self.posLabel.config(text=f"Current position: {self.get_position} mm")
        self.posLabel.grid(column=self.col, row=5, padx=10, pady=10)

    def blink(self):
        self.posLabel.config(text = "It's me!")

    def wait_for_stop(self):
        pass
    
    @property
    def convert(self):
        return 1

# Class of the main app window. It handles the UI, initialization of stages and popup windows like Mapper.
class Stage_app(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self._devices = Thorlabs.list_kinesis_devices()
        self.stage_list = []
        self._idlist = []
        self.virtual_stage_list = []
        self._virtual_idlist = []
        self.mapper_control = 0
        self.label_namelist = self._idlist+self._virtual_idlist
        self.mapper_button_present = False

        for i in range(len(self._devices)):
            self._idlist.append(self._devices[i][0])

        self.resolution_picker()
        
        self.grid()
        print(f"found stages: {self._idlist + self._virtual_idlist}")

        self.stage_pick_label = tk.Label(text="Stages found:")
        self.stage_pick_label.grid(column=0, row=0, padx=10, pady=10)


        self.open_mapper_button = tk.Button(master=self, text="Open Mapper", command=self.open_mapper, height=2, width=10)
        self.open_mapper_button.grid(column=0, row=3, padx=10, pady=10)

        self.reload_stages_button = tk.Button(master=self, text="Reload stages", command=self.stage_reload, height=2, width=10)
        self.reload_stages_button.grid(column=0, row=2, padx=10, pady=10)

        self.add_virtual_stage_button = tk.Button(master=self,text = "Add virtual stage",command=self.add_virtual_stage)
        self.add_virtual_stage_button.grid(column=0,row=1,padx=10,pady=10)


        self.initialize_stages(add_virtual=False)
        
        


    def add_virtual_stage(self):
        if len(self._virtual_idlist) < 5:
            self._virtual_idlist.append(f"VStage{len(self._virtual_idlist)}")
            self.initialize_stages(add_virtual=True)
        else: 
            print("Cant add more virtual stages than 2!")


    def stage_finish(self,close_virtual:bool):
        try:
            if close_virtual == True:
                for i in range(len(self._virtual_idlist)):
                    self._virtual_idlist.pop()
                    self.stage_list.pop()
            else:
                for i in range(len(self._idlist)):
                    self.stage_list[i].close()
        except:
            pass

    def update_label_position(self):
        self.label_namelist = self._idlist + self._virtual_idlist
        self.reload_stages_button.grid(row=len(self.label_namelist)+2)
        self.add_virtual_stage_button.grid(row=len(self.label_namelist)+1)
        self.open_mapper_button.grid(row=len(self.label_namelist)+3)



    def stage_reload(self):
        self.stage_finish(close_virtual=True)
        self.stage_finish(close_virtual=False)
        self.destroy()
        self.__init__()

    def initialize_stages(self,add_virtual: bool):
        self.label_namelist = self._idlist + self._virtual_idlist
        self.label_list = deepcopy(self.label_namelist)

        if add_virtual:
            self.stage_list.append(VirtualStage(id=self._virtual_idlist[-1],col = len(self.stage_list)+1, frame=self,state="normal"))
            self.label_list.append(tk.Label(text=f"{len(self.label_namelist)-1}: {self._virtual_idlist[-1]}"))
            self.label_list[-1].grid(column=0, row = len(self.label_namelist),padx=10,pady=10)
            
            
        else:
            
            self.stage_finish(close_virtual=True)
            self.stage_finish(close_virtual=False)
            self.stage_list = []

            for i in range(len(self._idlist)):
                self.stage_list.append(ThorlabsStage(id=self._idlist[i],col = len(self.stage_list)+1, frame=self,state="normal"))
                self.label_list[i] = tk.Label(text=f"{i}: {self._idlist[i]}")
                self.label_list[i].grid(column=0, row = i+1,padx=10,pady=10)

            
        self.update_label_position()


    def resolution_picker(self):
        if len(self._idlist) == 2:
            self.geometry = "1200x400"
        elif len(self._idlist) == 1:
            self.geometry = "600x400"
        elif len(self._idlist) == 3:
            self.geometry = "1800x400"
        elif len(self._idlist) >3:
            self.geometry = "2400x400"

    def popup_choose_stages_for_mapping(self):
        self.popup = tk.Toplevel(self)
        self.popup.geometry = ("600x200")
        self.popup.title("Pre-mapping")
        self.choose_stages_label = tk.Label(self.popup,text="Choose stages for mapping:")
        self.choose_stages_label.grid(column=0,row=0,padx=10,pady=10)
        self.checkbox_list = []
        self.checkbox_var_list = []
        
        for i in range(len(self.stage_list)):
            self.checkbox_var_list.append(tk.IntVar())
            self.checkbox_list.append(tk.Checkbutton(self.popup,text = self.label_namelist[i],variable=self.checkbox_var_list[i],onvalue=1, offvalue=0))
            self.checkbox_list[i].grid(column=0, row= i+1,padx=10,pady=10)
        self.submit_stages_for_mapping_button = tk.Button(self.popup, text="Submit",command=self.popup.destroy)
        self.submit_stages_for_mapping_button.grid(column = 0, row= len(self.stage_list)+2,padx=10,pady=10)

    def popup_choose_stages_for_mapping_close(self):
        for i in range(len(self.checkbox_var_list)):
            del(i)
        self.popup.destroy()


    def open_mapper(self):
        try:
            if self.mapper_window.state() == 'normal':
                messagebox.showinfo("Mapping Not Possible", "Mapper is already open!")
        except:
                if len(self.stage_list) >= 2:
                    self.popup_choose_stages_for_mapping()
                    self.wait_window(self.popup)
                    self.stages_for_mapping = []
                    self.stages_for_mapping_namelist = []
                    for i in range(len(self.checkbox_var_list)):
                        if self.checkbox_var_list[i].get() == 1:
                            
                            self.stages_for_mapping.append(self.stage_list[i])
                            self.stages_for_mapping_namelist.append(self.label_namelist[i])
                    
                else:  # Require at least two stages for mapping
                    self.stages_for_mapping = self.stage_list

                if len(self.stages_for_mapping) != 2:
                        messagebox.showinfo("Mapping Not Possible", "Two stages required for mapping!")
                        self.popup_choose_stages_for_mapping_close()
                        
                        return

                self.mapper_window = tk.Toplevel(self)
                self.mapper_window.title(f"Mapping with stages: {self.stages_for_mapping_namelist[0]}, {self.stages_for_mapping_namelist[1]}")
                self.mapper = Mapper(self.stages_for_mapping)
                self.mapperUI = MapperUI(frame=self.mapper_window,mapper=self.mapper)
            
            
# Mapper is a class to handle the mapping process (not the UI of Mapper!). It handles the simultanous movement of stages,
# creating list of points to map, starting the mapping process etc.
class Mapper():
    def __init__(self, stages):
        self.stages = stages
        self.mapping_points_on_map = 0
        self.map_list = []
        self.circle_id_list = []

        self.x_step = 0
        self.y_step = 0
        self.stage_x = self.stages[0]
        self.stage_y = self.stages[1]


    def move_to_position(self, x, y):
        motor_x = x / 10
        motor_y = y / 10
        self.move_two_at_once((motor_x,motor_y))

    def start_mapping(self):
        self.mapping_terminated = False
        self.mapping_thread = threading.Thread(target=self.mapping_process)
        self.mapping_thread.start()

    def create_map_list(self,map_parameters):
        self.map_list = []
        x_range,y_range,x_points,y_points = map_parameters
        try:
            x_step = x_range / (x_points - 1)
            y_step = y_range / (y_points - 1)
        except:
            if x_points == 1:
                x_step = 0
            if y_points == 1:
                y_step = 0
            
        motor_x = self.converted_position(self.stage_x)
        motor_y = self.converted_position(self.stage_y)
            
        for i in range(x_points):
            for j in range(y_points):
                x_coord = motor_x + i * x_step
                y_coord = motor_y + j * y_step
                self.map_list.append((x_coord,y_coord))
        return self.map_list

    def mapping_process(self):
        self.create_map_list()
        for coordinate in self.map_list:
            if coordinate[0]> 25 or coordinate[0] < 0 or coordinate[1] > 25 or coordinate[1] < 0:
                proceed = messagebox.askyesno("Out of bounds!", "Mapping area is out of bounds! Some points will be lost. Proceed anyway?")
                if proceed == False:
                    return
                else:
                    break
        for coordinate in self.map_list:
            if self.mapping_terminated:
                return
            print(f"Moving to point: ({round(coordinate[0],3)}, {coordinate[1]})")
            self.move_two_at_once(coordinate)
        print("Mapping finished :)")

    def get_stages(self):
        return self.stages
    
    def converted_position(self,stage):
        return stage.get_position/stage.convert

    def move_two_at_once(self,endlist):
        self.stage_x.move(endlist[0],check=False,update_now=False)
        self.stage_y.move(endlist[1],check=False,update_now=False)

        self.stage_x.wait_for_stop()
        self.stage_y.wait_for_stop()

    def move_two_at_once_to_00(self):
        self.stage_x.move(0,check=False,update_now=False)
        self.stage_y.move(0,check=False,update_now=False)
        
        self.stage_x.wait_for_stop()
        self.stage_y.wait_for_stop()


# MapperUI is the class that is responsible for the UI of mapping process. It communicates with Mapper class,
# handles all the button commands, updates Labels, shows the grid of points etc.
class MapperUI(Mapper):
    def __init__(self,frame,mapper: Mapper):
            self.max_range = 25.2
            self.square_count = 125
            self.square_size = self.max_range * 10 / self.square_count
            self.map_size = self.square_count * self.square_size
            self.marker_on_map = 0
            self.mapper = mapper
            super().__init__(self.mapper.get_stages())
            self.frame = frame

            self.x_range = tk.StringVar(self.frame,"0")
            self.x_range.trace_add("write",self.update_canvas)

            self.y_range = tk.StringVar(self.frame,"0")
            self.y_range.trace_add("write",self.update_canvas)

            self.x_points = tk.StringVar(self.frame,"0")
            self.x_points.trace_add("write",self.update_canvas)

            self.y_points = tk.StringVar(self.frame,"0")
            self.y_points.trace_add("write",self.update_canvas)

            self.selected_point = None

            kill_button = tk.Button(self.frame, text="Kill Mapping", command=self.kill_mapping)
            kill_button.grid(row=5, column=0, padx=10, pady=10)
            self.build_ui()
            self.build_canvas()
            self.update_canvas_marker()


    def create_map_list(self):
        try:
            x_range = float(self.x_range.get())
            y_range = float(self.y_range.get())
            x_points = int(self.x_points.get())
            y_points = int(self.y_points.get())
            self.x_step = x_range/x_points
            self.y_step = y_range/y_points

            map_parameters = [x_range,y_range,x_points,y_points]

            self.map_list = super().create_map_list(map_parameters)
            self.update_step_label(self.x_step,self.y_step)
            
        except:
            print("Input all variables! Grid not created")

    def move_two_at_once(self, endlist):
        self.current_task_label.config(text="Moving...")
        super().move_two_at_once(endlist)
        self.update_canvas_marker()
        self.update_position_labels()
        self.current_task_label.config(text="Idle")


    def move_two_at_once_to_00(self):
        self.current_task_label.config(text="Moving...")
        super().move_two_at_once_to_00()
        self.update_canvas_marker()
        self.update_position_labels()
        self.current_task_label.config(text="Idle")

    def move_to_position(self, x, y):
        self.current_task_label.config(text="Moving...")
        super().move_to_position(x, y)
        self.update_canvas_marker()
        self.update_position_labels()
        self.current_task_label.config(text="Idle")

    def mapping_process(self):
        super().mapping_process()
        self.update_canvas_marker()
        self.update_position_labels()


    def converted_position(self,stage):
        return stage.get_position/stage.convert

    def build_canvas(self):
        self.map_canvas = tk.Canvas(self.frame, width=int(self.map_size), height=int(self.map_size), bg="white")
        self.map_canvas.grid(row=0, column=0, padx=10, pady=10)
        self.map_canvas.bind("<Button-1>", self.on_canvas_click)

        for i in range(0, int(self.map_size), int(self.square_size)):
            for j in range(0, int(self.map_size), int(self.square_size)):
                square_id = f"square_{i}_{j}"
                
                self.map_canvas.create_rectangle(i, j, i + int(self.square_size), j + int(self.square_size),
                                                 fill="lightgray", outline="black", tags=square_id)

                self.map_canvas.tag_bind(square_id, "<Button-1>", lambda event, x=i, y=j: self.move_to_position(x, y))

                self.map_canvas.tag_bind(square_id, "<Enter>", lambda event, x=i, y=j: self.show_coordinates(x, y))

                self.map_canvas.tag_bind(square_id, "<Leave>", lambda event: self.clear_coordinates())

                
    def build_ui(self):
        self.coordinates_label = tk.Label(self.frame, text="", anchor="w")
        self.coordinates_label.grid(row=1, column=0, padx=10, pady=5, sticky="ew")


        self.curr_x_label = tk.Label(self.frame, text=f"Current X: {round(self.converted_position(self.stage_x),3)}mm")
        self.curr_x_label.grid(row = 2,column=0,padx=10,pady=10)
        
        self.curr_y_label = tk.Label(self.frame, text = f"Current Y: {round(self.converted_position(self.stage_y),3)}mm")
        self.curr_y_label.grid(row = 3,column=0,padx=10,pady=10)


        x_range_label = tk.Label(self.frame, text="X Range (mm):")
        x_range_label.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        self.x_range_entry = tk.Entry(self.frame, textvariable=self.x_range)
        #self.x_range_entry.insert(0,"") 
        self.x_range_entry.grid(row=1, column=2, padx=10, pady=5)


        y_range_label = tk.Label(self.frame, text="Y Range (mm):")
        y_range_label.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        self.y_range_entry = tk.Entry(self.frame, textvariable=self.y_range)
        #self.y_range_entry.insert(0, 0) 
        self.y_range_entry.grid(row=2, column=2, padx=10, pady=5)


        x_points_label = tk.Label(self.frame, text="X Points:")
        x_points_label.grid(row=3, column=1, padx=10, pady=5, sticky="w")
        self.x_points_entry = tk.Entry(self.frame, textvariable=self.x_points)
        self.x_points_entry.grid(row=3, column=2, padx=10, pady=5)


        y_points_label = tk.Label(self.frame, text="Y Points:")
        y_points_label.grid(row=4, column=1, padx=10, pady=5, sticky="w")
        self.y_points_entry = tk.Entry(self.frame, textvariable=self.y_points)
        self.y_points_entry.grid(row=4, column=2, padx=10, pady=5)


        start_button = tk.Button(self.frame, text="Start Mapping", command=self.start_mapping)
        start_button.grid(row=4, column=0, padx=10, pady=10)

        x_step_label = tk.Label(self.frame,text="X step:")
        x_step_label.grid(row=5,column=1,padx=10,pady=5,sticky="w")
        self.x_step_calc = tk.Label(self.frame, text=self.x_step)
        self.x_step_calc.grid(row=5, column=2, padx=10, pady=0)

        y_step_label = tk.Label(self.frame,text="Y step:")
        y_step_label.grid(row=6,column=1,padx=10,pady=5,sticky="w")
        self.y_step_calc = tk.Label(self.frame, text=self.y_step)
        self.y_step_calc.grid(row=6, column=2, padx=10, pady=0)

        self.refresh_button = tk.Button(self.frame,text="Refresh grid",command=self.update_canvas)
        self.refresh_button.grid(row=0,column=1,pady=10,padx=10,columnspan=2)

        self.current_task_label = tk.Label(self.frame,text="Idle")
        self.current_task_label.grid(row = 6, column=0,padx=10,pady=10)

        self.go_to_00_button = tk.Button(self.frame, text="Go to (0,0)",command=self.move_two_at_once_to_00)
        self.go_to_00_button.grid(row = 7, column=0,padx=10,pady=10)

    def clear_coordinates(self):
        self.coordinates_label.config(text="")

    def kill_mapping(self):
        self.mapping_terminated = True
        print("Mapping process has been terminated.")
        self.current_task_label.config(text="Idle")

    def show_coordinates(self, x, y):
        self.coordinates_label.config(text=f"Cursor: X: {x / 10}mm, Y: {y / 10}mm")

    def update_canvas_marker(self):
        x = self.converted_position(self.stage_x) * 10
        y = self.converted_position(self.stage_y) * 10
        

        if self.marker_on_map == 0:
            self.current_marker = self.map_canvas.create_oval(x-5,y+5,x+5,y-5,fill="red",tags="current marker")
            
            self.marker_on_map = 1
        else:
            #self.map_canvas.tag_bind("current marker", "<Enter>", lambda event, x=x, y=y: self.show_coordinates(x, y))
            #self.map_canvas.tag_bind("current marker", "<Leave>", lambda event: self.clear_coordinates())
            self.map_canvas.move(self.current_marker,x-self.prev_position[0],y-self.prev_position[1])

        self.prev_position = (x,y)
        self.marker_on_map = 1
             

    def update_step_label(self,xstep,ystep):
        self.x_step_calc.config(text=round(xstep,3))
        self.y_step_calc.config(text=round(ystep,3))
        
    
    def update_canvas(self,*args):
        self.create_map_list()
        if self.mapping_points_on_map == 1:
            for id in self.circle_id_list:
                self.map_canvas.delete(id)
        for coordinate in self.map_list:
            x,y = coordinate
            circle_id = f"circle_{x}_{y}"
            self.circle_id_list.append(circle_id)
            self.map_canvas.create_oval(10*x-3,10*y+3,10*x+3,10*y-3,fill="blue",tags=circle_id)
            self.map_canvas.tag_bind(circle_id, "<Button-1>", lambda event, x=x, y=y: self.move_to_position(10*x, 10*y))
            self.map_canvas.tag_bind(circle_id, "<Enter>", lambda event, x=x, y=y: self.show_coordinates(x, y))
            self.map_canvas.tag_bind(circle_id, "<Leave>", lambda event: self.clear_coordinates())
            self.mapping_points_on_map = 1


    def update_position_labels(self):
        self.curr_x_label.config(text=f"Current X: {round(self.converted_position(self.stage_x),3)} mm")
        self.curr_y_label.config(text=f"Current Y: {round(self.converted_position(self.stage_y),3)} mm")

    def on_canvas_click(self, event):
        self.selected_point = (event.x, event.y)


if __name__ == "__main__":
    app = Stage_app()
    app.title("Control Panel for XYMapper")
    app.iconbitmap("KDC_icon_ico.ico")

    app.mainloop()






# The Diagram of Classes
    """
          +----------------+                      
          |   Stage(ABC)   |                  
          +----------------+                  
                 ^
                 |
         +-------+--------+
         |                |
+----------------+ +-----------------+
| ThorlabsStage  | |  VirtualStage   |
+----------------+ +-----------------+

        +----------------+
        |     Mapper     |
        +----------------+
                 ^
                 |
                 | 
                 |               
         +-----------------+
         |    MapperUI     |
         +-----------------+


          
          +-----------------+
          |   tkinter.Tk    |
          +-----------------+
                   ^
                   |
                   |
          +-----------------+
          |    Stage_app    |
          +-----------------+
    
    
    """

# ADydnianski, 05.06.2024