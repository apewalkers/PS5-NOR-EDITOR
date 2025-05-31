import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
from PIL import Image, ImageTk

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and PyInstaller"""
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Usage
img_path = resource_path("Data/QR1.png")

class CriticalInfoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Nor Data Editor")
        self.geometry("850x800")
        self.configure(bg="#1E1E1E")

        #img_path = resource_path("Data/QR1.png")
        #image = Image.open(img_path)
        #photo = ImageTk.PhotoImage(image)

        #label = ttk.Label(self, image=photo)
        #label.image = photo  # Keep a reference!
        #label.pack()


        self.style = ttk.Style(self) # Store the style object as an instance attribute
        self.setup_styles()
        self.setup_pre_configs() # New method to define pre-configured data

        self.critical_map = {

            #EMC
            'Active_Slot': {'o': 0x001000, 'l': 1, 't': 'b', 'n': 'EMC slot'},
            'REGION': {'o': 0x1C7236, 'l': 2, 't': 's', 'n': 'Region code'}, # This is the field that will be derived from SKU for display

            #Console
            'SKU_Type': {'o': 0x1C7038, 'l': 1, 't': 'b', 'n': 'SKU'},
            'Revision': {'o': 0x1C7011, 'l': 1, 't': 'b', 'n': 'Revision'},
            'SN': {'o': 0x1C7210, 'l': 17, 't': 's', 'n': 'Console Serial'}, # 20
            'SKU': {'o': 0x1C7230, 'l': 13, 't': 's', 'n': 'SKU Version'},
                   

            #Console Specific 
            'SOCUID': {'o': 0x1C7260, 'l': 16, 't': 's', 'n': 'SOC UUID'},
            'KIBAN': {'o': 0x1C7250, 'l': 13, 't': 's', 'n': 'Kiban ID'},
            'BOARD_ID': {'o': 0x1C4000, 'l': 8, 't': 's', 'n': 'Board ID'},
            'MB_SN': {'o': 0x1C7200, 'l': 16, 't': 's', 'n': 'Motherboard Serial'},
            
            # MAC Address
            'EthernetMAC': {'o': 0x1C4020, 'l': 6, 't': 'b', 'n': 'LAN MAC Address'},
            'WLAN_MAC': {'o': 0x1C73C0, 'l': 6, 't': 'b', 'n': 'WLAN MAC'},
            'BD_MAC1': {'o': 0x1C73C6, 'l': 6, 't': 'b', 'n': 'BD MAC 1'},
            'BD_MAC2': {'o': 0x1C73CC, 'l': 6, 't': 'b', 'n': 'BD MAC 2'},

            #Flags
            'IDU': {'o': 0x1C9600, 'l': 1, 't': 'b', 'n': 'IDU (Kiosk mode)'}
        }
            # Map of critical offsets from Wee-Tools

        self.critical_map_ordered = [
            ('HEADER', 'EMC'),
            ('FIELD', 'Active_Slot'),
            ('FIELD', 'REGION'),

            ('HEADER', 'Console'),
            ('FIELD', 'SKU_Type'),
            ('FIELD', 'Revision'),
            ('FIELD', 'SN'),
            ('FIELD', 'SKU'),

            ('HEADER', 'Console Specific'),
            ('FIELD', 'SOCUID'),
            ('FIELD', 'KIBAN'),
            ('FIELD', 'BOARD_ID'),
            ('FIELD', 'MB_SN'),

            ('HEADER', 'MAC Address'),
            ('FIELD', 'EthernetMAC'),
            ('FIELD', 'WLAN_MAC'),
            ('FIELD', 'BD_MAC1'),
            ('FIELD', 'BD_MAC2'),

            ('HEADER', 'Flags'),
            ('FIELD', 'IDU'),
        ]

        self.regions = {
            '00': 'Japan',
            '01': 'US, Canada (North America)',
            '15': 'US, Canada (North America)',
            '02': 'Australia / New Zealand (Oceania)',
            '03': 'U.K. / Ireland',
            '16': 'Europe / Middle East / Africa',
            '04': 'Europe / Middle East / Africa',
            '05': 'Korea (South Korea)',
            '06': 'Southeast Asia / Hong Kong',
            '07': 'Taiwan',
            '08': 'Russia, Ukraine, India, Central Asia',
            '09': 'Mainland China',
            '11': 'Mexico, Central America, South America',
            '14': 'Mexico, Central America, South America',
            '18': 'Singapore, Korea, Asia'
        }

        self.model_variant_1 = {
            0x01: "Slim",
            0x02: "Original Disc",
            0x03: "Original Digital"
        }
        self.model_variant_2 = {
            0x89: "Disc",
            0x8D: "Digital"
        }
        self.active_slot_map = {
            0x00: "A",
            0x80: "B"
        }

        self.idu_map = {
            0xFF: "Off",
            0x01: "On"
        }

        self.data = bytearray()

        self.fields = {}
        self.harvest_checkbox_vars = {} # To store BooleanVars for harvest selection dialog
        self.selected_harvest_fields = set() # To store keys of fields selected for harvest

        self.original_file_path = None
        self.output_file_path = None 
        self.harvest_file_path = None

        self.create_widgets()

    def setup_styles(self):
        """Configures the ttk styles for a dark theme."""
        self.style.theme_use('clam')  

        # Define common colors
        bg_dark = "#1E1E1E"          # Main background
        bg_medium = "#2C2C2C"        # Frame/widget background
        bg_light = "#3A3A3A"         # Entry/Combobox field background
        fg_text = "#E0E0E0"          # Light text color
        accent_color = "#6A5ACD" # A subtle purple for highlights/active states
        border_color = "#444444"

        # General TFrame style
        self.style.configure("TFrame", background=bg_medium)

        # Label style
        self.style.configure("TLabel", background=bg_medium, foreground=fg_text, font=('Inter', 8))

        # Header Label style (New)
        self.style.configure("Header.TLabel", background=bg_medium, foreground=accent_color,
                             font=('Inter', 8, 'bold'), anchor='w')

        # Checkbutton style
        self.style.configure("TCheckbutton",
                             background=bg_medium,
                             foreground=fg_text,
                             font=('Inter', 8),
                             focusthickness=0,
                             relief="flat")
        self.style.map("TCheckbutton",
                       background=[('active', bg_medium)],
                       foreground=[('active', accent_color)])

        # Button style
        self.style.configure("TButton",
                             background=accent_color,
                             foreground="#FFFFFF",
                             font=('Inter', 8, 'bold'),
                             borderwidth=0,
                             focusthickness=0,
                             relief="flat",
                             padding=(10, 5))
        self.style.map("TButton",
                       background=[('active', '#7B68EE'), ('pressed', '#5C4BB3')],
                       foreground=[('active', '#FFFFFF')])

        # Entry style
        self.style.configure("Dark.TEntry",
                             fieldbackground=bg_light,
                             background=bg_light,
                             foreground=fg_text,
                             bordercolor=border_color,
                             lightcolor=border_color,
                             darkcolor=border_color,
                             insertcolor=fg_text,
                             padding=5,
                             borderwidth=1,
                             relief="flat")
        self.style.map("Dark.TEntry",
                       fieldbackground=[("focus", bg_light)],
                       bordercolor=[("focus", accent_color)],
                       lightcolor=[("focus", accent_color)],
                       darkcolor=[("focus", accent_color)])

        self.style.configure("Dark.TCombobox",
                             fieldbackground=bg_light,
                             background=bg_medium, # Background of the combobox itself
                             foreground=fg_text,
                             selectbackground=accent_color,
                             selectforeground="#FFFFFF",
                             bordercolor=border_color,
                             arrowcolor=fg_text,
                             padding=5,
                             relief="flat")
        self.style.map("Dark.TCombobox",
                       fieldbackground=[("readonly", bg_light)],
                       background=[("readonly", bg_medium)],
                       foreground=[("readonly", fg_text)],
                       selectbackground=[("readonly", accent_color)],
                       selectforeground=[("readonly", "#FFFFFF")],
                       bordercolor=[("focus", accent_color)],
                       arrowcolor=[("focus", accent_color)])

        
        self.style.configure("Dark.TLabel",
                             background=bg_medium,
                             foreground=fg_text,
                             font=('Inter', 8))

        
        self.style.configure("TListbox",
                             font=('Inter', 8), 
                             background=bg_medium,  
                             foreground=fg_text,   
                             selectbackground=accent_color, 
                             selectforeground="#FFFFFF",     
                             bordercolor=border_color,      
                             relief="solid",                 
                             borderwidth=1                   
                            )
        self.style.map("TListbox",
                       background=[('active', bg_light)],    
                       foreground=[('active', fg_text)],     
                       selectbackground=[('!active', accent_color)], 
                       selectforeground=[('!active', "#FFFFFF")]  
                      )


        # Scrollbar style
        self.style.configure("Vertical.TScrollbar",
                             background=bg_medium,
                             troughcolor=bg_dark,
                             bordercolor=border_color,
                             arrowcolor=fg_text,
                             relief="flat")
        self.style.map("Vertical.TScrollbar",
                       background=[('active', accent_color)])

        # Separator style
        self.style.configure("TSeparator", background=border_color)

    def setup_pre_configs(self):
        """Defines the pre-configured data sets."""
        # Helper functions to convert raw hex/byte values to display format for pre-configs
        def hex_to_ascii_raw(hex_str):
            try:
                if len(hex_str) % 2 != 0: hex_str = '0' + hex_str
                return bytes.fromhex(hex_str).decode('ascii').rstrip('\x00')
            except Exception:
                return hex_str # Return original hex if decoding fails

        
        self.pre_configs = {
        'edm-010': {
            'Active_Slot': '80',
            'BD_MAC1': 'BC3329136342',
            'BD_MAC2': 'BC3329136343',
            'BOARD_ID': '3002020101010501',
            'EthernetMAC': '5C9666255182',
            'IDU': 'FF',
            'KIBAN': '30303030303237343138393836',
            'MB_SN': '34303032394230303633323035364130',
            'REGION': '3032',
            'Revision': '02',
            'SKU': '4346492D313130324120303100',
            'SKU_Type': '89',
            'SN': '463231413031424D383131333835393239',
            'SOCUID': 'E96F0015A292E7F17C118BB8F25F9EE7',
            'WLAN_MAC': 'BC3329136341'
        },
        'edm-020': {
            'Active_Slot': '80',
            'BD_MAC1': '5C9666F99010',
            'BD_MAC2': '5C9666F99011',
            'BOARD_ID': '3002020101030501',
            'EthernetMAC': '5C843C9B8C0E',
            'IDU': 'FF',
            'KIBAN': '30303030303237343138393930',
            'MB_SN': '41423034323730303433323034344230',
            'REGION': '3135',
            'Revision': '03',
            'SKU': '4346492D313131354220303158',
            'SKU_Type': '8D',
            'SN': '414C303937343137363500000000000000',
            'SOCUID': '5882F81BF69AB052F674E94D4F676039',
            'WLAN_MAC': '5C9666F9900F'
        },
        'edm-030_69G': {
            'Active_Slot': '00',
            'BD_MAC1': '04F778B623EA',
            'BD_MAC2': '04F778B623EB',
            'BOARD_ID': '3002030101010501',
            'EthernetMAC': '0C704375DAF1',
            'IDU': 'FF',
            'KIBAN': '30303030303237343235323339',
            'MB_SN': '34303130314230303330393137324130',
            'REGION': '3032',
            'Revision': '02',
            'SKU': '4346492D3132303241205A3258',
            'SKU_Type': '89',
            'SN': '463333365A324835583130323532393136',
            'SOCUID': '0E719E4B35DD47711A925309E873EB55',
            'WLAN_MAC': '04F778B623E9'
        },
        'edm-031_61G': {
            'Active_Slot': '00',
            'BD_MAC1': '70662ACCE950',
            'BD_MAC2': '70662ACCE951',
            'BOARD_ID': '3002030101010501',
            'EthernetMAC': '84E657DD267F',
            'IDU': 'FF',
            'KIBAN': '30303030303237343139313432',
            'MB_SN': '34303332364130303234353233304130',
            'REGION': '3032',
            'Revision': '02',
            'SKU': '4346492D313230324120303100',
            'SKU_Type': '89',
            'SN': '46333241303153434E3131333937383837',
            'SOCUID': '9B5D4642A6081ACC7C08DAF6167E270F',
            'WLAN_MAC': '70662ACCE94F'
        },
        'edm-031_69G': {
            'Active_Slot': '80',
            'BD_MAC1': 'C84AA02322EA',
            'BD_MAC2': 'C84AA02322EB',
            'BOARD_ID': '3002030101010501',
            'EthernetMAC': 'C84AA0748D8F',
            'IDU': 'FF',
            'KIBAN': '30303030303237343139313432',
            'MB_SN': '34303330374230303135343335334130',
            'REGION': '3032',
            'Revision': '02',
            'SKU': '4346492D313230324120303100',
            'SKU_Type': '89',
            'SN': '46333243303153434E3131343535373931',
            'SOCUID': 'E4444B285145AD65F3C93210FCCD68A3',
            'WLAN_MAC': 'C84AA02322E9'
        },
        'edm-032_61G': {
            'Active_Slot': '80',
            'BD_MAC1': '5C843C5BB701',
            'BD_MAC2': '5C843C5BB702',
            'BOARD_ID': '3002030101010501',
            'EthernetMAC': '70662A1F06C5',
            'IDU': 'FF',
            'KIBAN': '30303030303237343139313432',
            'MB_SN': '34303133344330303032393432334130',
            'REGION': '3032',
            'Revision': '02',
            'SKU': '4346492D313230324120303100',
            'SKU_Type': '89',
            'SN': '46333236303153434E3131323736323634',
            'SOCUID': '5984FD17A0B11518ADD794651762801C',
            'WLAN_MAC': '5C843C5BB700'
        },
        'edm-032_69G': {
            'Active_Slot': '80',
            'BD_MAC1': '5C843C5BB701',
            'BD_MAC2': '5C843C5BB702',
            'BOARD_ID': '3002030101010501',
            'EthernetMAC': '70662A1F06C5',
            'IDU': 'FF',
            'KIBAN': '30303030303237343139313432',
            'MB_SN': '34303133344330303032393432334130',
            'REGION': '3032',
            'Revision': '02',
            'SKU': '4346492D313230324120303100',
            'SKU_Type': '89',
            'SN': '46333236303153434E3131323736323634',
            'SOCUID': '5984FD17A0B11518ADD794651762801C',
            'WLAN_MAC': '5C843C5BB700'
        },
        'edm-033_61G': {
            'Active_Slot': '80',
            'BD_MAC1': '70662A2ED857',
            'BD_MAC2': '70662A2ED858',
            'BOARD_ID': '3002030101010501',
            'EthernetMAC': '2C9E00FB41EA',
            'IDU': 'FF',
            'KIBAN': '30303030303237343139313139',
            'MB_SN': '34303139384430303335303331384130',
            'REGION': '3135',
            'Revision': '02',
            'SKU': '4346492D313231354120303158',
            'SKU_Type': '89',
            'SN': '463332393031374A423132383132393533',
            'SOCUID': '60F25DD162B8133CF493E9C0755EACD4',
            'WLAN_MAC': '70662A2ED856'
        },
        'edm-033_69G': {
            'Active_Slot': '80',
            'BD_MAC1': '70662A55AD94',
            'BD_MAC2': '70662A55AD95',
            'BOARD_ID': '3002030101010501',
            'EthernetMAC': '84E6574B7F17',
            'IDU': 'FF',
            'KIBAN': '30303030303237343139313432',
            'MB_SN': '34303139314530303133383433304130',
            'REGION': '3032',
            'Revision': '02',
            'SKU': '4346492D313230324120303100',
            'SKU_Type': '89',
            'SN': '46333241303153434E3131333538353234',
            'SOCUID': 'F503DB47ECEAE913787EFF930A7C7E77',
            'WLAN_MAC': '70662A55AD93'
        },
        'edm-040_J20H104': {
            'Active_Slot': '80',
            'BD_MAC1': '0C7043D078C7',
            'BD_MAC2': '0C7043D078C8',
            'BOARD_ID': '3002040101030501',
            'EthernetMAC': 'EC748CB3481F',
            'IDU': 'FF',
            'KIBAN': '30303030303237343235313136',
            'MB_SN': '34303534324430303031353239313030',
            'REGION': '3032',
            'Revision': '01',
            'SKU': '4346492D323030322041303100',
            'SKU_Type': '8D',
            'SN': '4634334130314E584D3130323937323836',
            'SOCUID': '17E7BDC193271AD5644D6E1DB0D71611',
            'WLAN_MAC': '0C7043D078C6'
        },
        'edm-040_aw-xm501': {
            'Active_Slot': '80',
            'BD_MAC1': 'E86E3A35703D',
            'BD_MAC2': 'E86E3A35703E',
            'BOARD_ID': '3002040101030501',
            'EthernetMAC': 'EC748CB46779',
            'IDU': 'FF',
            'KIBAN': '30303030303237343235313136',
            'MB_SN': '34303439374330303134303136303030',
            'REGION': '3032',
            'Revision': '01',
            'SKU': '4346492D323030322041303100',
            'SKU_Type': '8D',
            'SN': '4634334130314E584D3130333030373730',
            'SOCUID': 'FE1B394640F6D6E9B6FDAA25254B020B',
            'WLAN_MAC': 'E86E3A35703C'
        },
        'edm-30_61G': {
            'Active_Slot': '80',
            'BD_MAC1': '5C843C367483',
            'BD_MAC2': '5C843C367484',
            'BOARD_ID': '3002030101030501',
            'EthernetMAC': '70662AB432C6',
            'IDU': 'FF',
            'KIBAN': '30303030303237343139313135',
            'MB_SN': '34303131304130303133393933334230',
            'REGION': '3135',
            'Revision': '03',
            'SKU': '4346492D313231354220303158',
            'SKU_Type': '8D',
            'SN': '4633323830314D4B453131333531333932',
            'SOCUID': 'AC3BC6F5CE019165C0FC33E51507B86E',
            'WLAN_MAC': '5C843C367482'
        },
        'edm-41': {
            'Active_Slot': '00',
            'BD_MAC1': 'FFFFFFFFFFFF',
            'BD_MAC2': 'FFFFFFFFFFFF',
            'BOARD_ID': '3002040101030501',
            'EthernetMAC': 'B40AD8423D50',
            'IDU': 'FF',
            'KIBAN': 'FFFFFFFFFFFFFFFFFFFFFFFFFF',
            'MB_SN': 'FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF',
            'REGION': 'FFFF',
            'Revision': 'FF',
            'SKU': 'FFFFFFFFFFFFFFFFFFFFFFFFFF',
            'SKU_Type': 'FF',
            'SN': 'FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF',
            'SOCUID': 'FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF',
            'WLAN_MAC': 'FFFFFFFFFFFF'
        }
    }

    def create_widgets(self):
        """Creates and packs all the widgets in the application, respecting critical_map_ordered."""
        
        file_frame = ttk.Frame(self, padding=10)
        file_frame.pack(fill='x', padx=10, pady=5)

        
        ttk.Label(file_frame, text="Original File:").pack(side='left', padx=(0, 5))
        self.original_file_entry = ttk.Entry(file_frame, style="Dark.TEntry")
        self.original_file_entry.pack(side='left', fill='x', expand=True, padx=(0, 5))
        ttk.Button(file_frame, text="Browse", command=self.browse_original_file).pack(side='left', padx=5)

        
        ttk.Label(file_frame, text="   ").pack(side='left')  # simple spacer

        
        ttk.Label(file_frame, text="Harvest File:").pack(side='left', padx=(10, 5))
        self.harvest_file_entry = ttk.Entry(file_frame, style="Dark.TEntry")
        self.harvest_file_entry.pack(side='left', fill='x', expand=True, padx=(0, 5))
        ttk.Button(file_frame, text="Browse", command=self.browse_harvest_file).pack(side='left', padx=5)

        pre_config_save_frame = ttk.Frame(self, padding=10)
        pre_config_save_frame.pack(fill='x', padx=10, pady=5)

       
        ttk.Label(pre_config_save_frame, text="Pre-Configured:", style="Dark.TLabel").pack(side='left', padx=(0, 5))

        
        self.pre_config_combobox = ttk.Combobox(pre_config_save_frame, width=25, state="readonly", style="Dark.TCombobox")
        self.pre_config_combobox['values'] = ["Select a configuration"] + sorted(list(self.pre_configs.keys()))
        self.pre_config_combobox.set("Select a configuration")
        self.pre_config_combobox.pack(side='left', padx=(0, 5))
        self.pre_config_combobox.bind("<<ComboboxSelected>>", self.load_pre_config_values)


        # Separator label
        ttk.Label(pre_config_save_frame, text="|").pack(side='left', padx=5)

        
        spacer = ttk.Frame(pre_config_save_frame)
        spacer.pack(side='left', fill='x', expand=True)

        
        ttk.Button(pre_config_save_frame, text="Save As...", command=self.save_output_file_as).pack(side='right', padx=5)




        ttk.Separator(self, orient='horizontal', style="TSeparator").pack(fill='x', pady=10, padx=10)
        
        
        content_container = ttk.Frame(self, padding=10)
        content_container.pack(fill='both', expand=True, padx=10, pady=5)

        
        self.fields_frame = ttk.Frame(content_container, padding=10)
        self.fields_frame.pack(side='left', fill='both', expand=True)

        
        right_container = ttk.Frame(content_container)
        right_container.pack(side='right', fill='y')

        
        self.footer_frame = ttk.Frame(right_container, padding=(10, 5), relief="flat")
        self.footer_frame.pack(side='bottom', anchor='se', padx=(10, 0), pady=(5, 10))

        
        self.fields_frame = ttk.Frame(content_container, padding=10)
        self.fields_frame.pack(side='left', fill='both', expand=True)


        
        canvas_bg_color = self.style.lookup("TFrame", "background")
        canvas = tk.Canvas(self.fields_frame, bg=canvas_bg_color, highlightthickness=0)

        # Scrollbar, initially not packed
        #scrollbar = ttk.Scrollbar(self.fields_frame, orient="vertical", command=canvas.yview, style="Vertical.TScrollbar")
        #canvas.configure(yscrollcommand=scrollbar.set)

        # Frame inside canvas to hold dynamic content
        self.data_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=self.data_frame, anchor="nw")

        #def update_scroll_region(event=None):
         #   canvas.configure(scrollregion=canvas.bbox("all"))
         #   bbox = canvas.bbox("all")
         #   if bbox:
         #       needs_scrollbar = bbox[3] > canvas.winfo_height()
         #       if needs_scrollbar:
         #           if not scrollbar.winfo_ismapped():
         #               scrollbar.pack(side="right", fill="y")
         #       else:
         #           if scrollbar.winfo_ismapped():
         #               scrollbar.pack_forget()

        
        #self.data_frame.bind("<Configure>", update_scroll_region)
        #canvas.bind("<Configure>", update_scroll_region)

        
        canvas.pack(side="left", fill="both", expand=True)

        
        #self.after(100, update_scroll_region)


        
        current_row = 0
        for item_type, item_name in self.critical_map_ordered:
            if item_type == 'HEADER':
                # Add a header label
                header_label = ttk.Label(self.data_frame, text=item_name.upper(), style="Header.TLabel")
                header_label.grid(row=current_row, column=0, columnspan=2, sticky='ew', pady=(8, 5)) # Add top padding
                current_row += 1
            elif item_type == 'FIELD':
                key = item_name
                info = self.critical_map[key]
                
                label = ttk.Label(self.data_frame, text=info['n'] + ":")
                label.grid(row=current_row, column=0, sticky='w', pady=4, padx=(0, 5))

                if key == "REGION":
                    combo = ttk.Combobox(self.data_frame, width=30, state="readonly", style="Dark.TCombobox")
                    combo['values'] = [f"{code} - {name}" for code, name in self.regions.items()]
                    combo.grid(row=current_row, column=1, sticky='ew', padx=(0, 5))
                    self.fields[key] = combo

                elif key == "Active_Slot":
                    combo = ttk.Combobox(self.data_frame, width=30, state="readonly", style="Dark.TCombobox")
                    combo['values'] = [f"0x{key:02X} - {val}" for key, val in self.active_slot_map.items()]
                    combo.grid(row=current_row, column=1, sticky='ew', padx=(0, 5))
                    self.fields[key] = combo

                elif key == "Revision":
                    combo = ttk.Combobox(self.data_frame, width=30, state="readonly", style="Dark.TCombobox")
                    combo['values'] = [f"0x{key:02X} - {val}" for key, val in self.model_variant_1.items()]
                    combo.grid(row=current_row, column=1, sticky='ew', padx=(0, 5))
                    self.fields[key] = combo

                elif key == "SKU_Type":
                    combo = ttk.Combobox(self.data_frame, width=30, state="readonly", style="Dark.TCombobox")
                    combo['values'] = [f"0x{key:02X} - {val}" for key, val in self.model_variant_2.items()]
                    combo.grid(row=current_row, column=1, sticky='ew', padx=(0, 5))
                    self.fields[key] = combo

                elif key == "IDU":
                    combo = ttk.Combobox(self.data_frame, width=30, state="readonly", style="Dark.TCombobox")
                    combo['values'] = ["On", "Off"]
                    combo.grid(row=current_row, column=1, sticky='ew', padx=(0, 5))
                    self.fields[key] = combo

                else:
                    entry = ttk.Entry(self.data_frame, width=40, style="Dark.TEntry")
                    entry.grid(row=current_row, column=1, sticky='ew', padx=(0, 5))
                    self.fields[key] = entry
                
                current_row += 1
        
        
        self.data_frame.grid_columnconfigure(1, weight=1)

       
        
        self.footer_frame = ttk.Frame(content_container, padding=(10, 5), relief="flat")
        self.footer_frame.pack(side='right', fill='y', padx=(10, 0), pady=(5, 10))

        self.footer_frame.grid_columnconfigure(0, weight=1) # Center the text and QR code

        # "Thank You!" text
        thank_you_label = ttk.Label(self.footer_frame, text="Dony's PS5 NOR Editor\n\n\n "
                "How To:\n\n"
                "- Click 'Browse Original File' to select\n"
                "  your own console's original NOR dump.\n\n"
                "  This file contains your unique console\n"
                "  data. Once selected, you can adjust\n"
                "  any necessary settings before\n"
                "  proceeding.\n\n"
                "Alternative Option:\n\n"
                "- If you don't have your original NOR,\n"
                "  use a verified working dump from:\n"
                "  \\Data\\NOR Files\\ as the base\n"
                "  (Original File). These have been tested\n"
                "  and are known to work across\n"
                "  compatible consoles.\n\n"
                "- Use the 'Harvest' function to extract\n"
                "  your console-specific data from your\n"
                "  inputs and merge it into the verified\n"
                "  NOR. This will generate a new, clean,\n"
                "  working NOR image customized for your\n"
                "  console.\n\n"
                "     Show your Support\n     https://www.paypal.com/paypalme/dannyjohn08\n     https://github.com/apewalkers/",
                                     font=('Inter', 10, 'bold'), foreground="#E0E0E0", background=self.style.lookup("TFrame", "background"))
        thank_you_label.grid(row=0, column=0, pady=(5, 0), sticky='s')

        
        try:
            qr_path = resource_path('Data/qr1.png')

            self.qr_image_pil = Image.open(qr_path)
            self.qr_image_pil = self.qr_image_pil.resize((70, 70), Image.Resampling.LANCZOS)
            self.qr_image_tk = ImageTk.PhotoImage(self.qr_image_pil)

            self.qr_float_frame = ttk.Frame(self, padding=5, style="TFrame")
            self.qr_float_frame.place(relx=0.98, rely=0.98, anchor='se')

            qr_label = ttk.Label(self.qr_float_frame, image=self.qr_image_tk,
                                background=self.style.lookup("TFrame", "background"))
            qr_label.pack(pady=(0, 2))

        except Exception as e:
            print(f"Error loading QR image: {e}")


            #qr_text_label = ttk.Label(self.qr_float_frame, text="Scan to Support\nhttps://www.paypal.com/paypalme/dannyjohn08", 
            #                        font=('Inter', 8), 
            #                        foreground="#E0E0E0", 
            #                        background=self.style.lookup("TFrame", "background"))
            #qr_text_label.pack()

            # Text under the QR code
            #qr_text_label = ttk.Label(self.footer_frame, text=(
            #    "How To:\n\n"
            #    "- Click 'Browse Original File' to select\n"
            #    "  your own console's original NOR dump.\n\n"
            #    "  This file contains your unique console\n"
            #    "  data. Once selected, you can adjust\n"
            #    "  any necessary settings before\n"
            #    "  proceeding.\n\n"
            #    "Alternative Option:\n\n"
            #    "- If you don't have your original NOR,\n"
            #    "  use a verified working dump from:\n"
            #    "  \\Data\\NOR Files\\ as the base\n"
            #    "  (Original File). These have been tested\n"
            #    "  and are known to work across\n"
            #    "  compatible consoles.\n\n"
            #    "- Use the 'Harvest' function to extract\n"
            #    "  your console-specific data from your\n"
            #    "  inputs and merge it into the verified\n"
            #    "  NOR. This will generate a new, clean,\n"
            #    "  working NOR image customized for your\n"
            #    "  console."
            #),
            #font=('Inter', 8),
            #foreground="#E0E0E0",
            #background=self.style.lookup("TFrame", "background"),
            #justify='left', wraplength=340)

            #qr_text_label.grid(row=2, column=0, pady=(2, 10), sticky='n')






        except FileNotFoundError:
            #messagebox.showwarning("Image Error", f"QR code image not found at: {qr_path}")
            # Optional: Display a placeholder or simply omit the QR code label
            qr_label = ttk.Label(self.footer_frame, text="MISSING FILES or Invalid Files", foreground="red", background=self.style.lookup("TFrame", "background"))
            qr_label.grid(row=1, column=0, pady=(5, 0))
        except Exception as e:
            messagebox.showwarning("Image Error", f"MISSING FILES: {e}")
            qr_label = ttk.Label(self.footer_frame, text="QR Code Error", foreground="red", background=self.style.lookup("TFrame", "background"))
            qr_label.grid(row=1, column=0, pady=(5, 0))
        # --- End of Footer modifications ---

    def browse_original_file(self):
        """Opens a file dialog to select the original file and then loads it automatically."""
        path = filedialog.askopenfilename(title="Select Original File")
        if path:
            self.original_file_path = path
            self.original_file_entry.delete(0, tk.END)
            self.original_file_entry.insert(0, path)
            self.load_original_file() # Automatically load the file

    def browse_harvest_file(self):
        """Opens a file dialog to select the harvest file and then opens the selection dialog."""
        path = filedialog.askopenfilename(title="Select Harvest File")
        if path:
            self.harvest_file_path = path
            self.harvest_file_entry.delete(0, tk.END)
            self.harvest_file_entry.insert(0, path)
            self.open_harvest_selection_dialog() # Open dialog after file is selected

    def save_output_file_as(self):
        """Opens a 'Save As' dialog and then saves the modified data to the chosen file."""
        if not self.data:
            messagebox.showerror("Error", "No data loaded to save.")
            return

        # Always open a Save As dialog
        path = filedialog.asksaveasfilename(title="Save Output File As",
                                            initialfile="_modified.bin",
                                            defaultextension=".bin",
                                            filetypes=[("Binary files", "*.bin"), ("All files", "*.*")])
        if path:
            self.output_file_path = path # Update the last saved path
            self._write_data_to_file(path)


    def _write_data_to_file(self, file_path):
        """Helper method to write the current data to a specified file path."""
        try:
            for key, info in self.critical_map.items():
                o = info['o']
                l = info['l']

                # Ensure we don't write beyond the current data length
                if o + l > len(self.data):
                    print(f"Warning: Data buffer too small for {key}. Skipping save for this field.")
                    continue

                if key == "REGION":
                    
                    val_str = self.fields[key].get().split(' ')[0]
                    if len(val_str) != 2:
                        raise ValueError(f"Invalid region code for {key}. Must be 2 hex characters.")
                    self.data[o:o + l] = bytes.fromhex(val_str)

                elif key == "Active_Slot":
                    text = self.fields[key].get()
                    hex_part = text.split(' ')[0]
                    val = int(hex_part, 16)
                    self.data[o] = val

                elif key == "BOARD_ID":
                    text = self.fields[key].get()
                    # Remove any non-hex characters if present (e.g., spaces)
                    text = ''.join(filter(str.isalnum, text)) 
                    
                    # Ensure even number of characters for hex conversion
                    if len(text) % 2 != 0:
                        text = '0' + text # Prepend '0' for odd length hex string
                    
                    val_bytes = bytes.fromhex(text)
                    
                    if len(val_bytes) < l:
                        val_bytes += b'\xFF' * (l - len(val_bytes)) # Pad with FF
                    elif len(val_bytes) > l:
                        val_bytes = val_bytes[:l] # Truncate if too long
                    self.data[o:o+l] = val_bytes

                elif key == "EthernetMAC" or key.startswith("WLAN_MAC") or key.startswith("BD_MAC"):
                    text = self.fields[key].get()
                    # Remove colons and spaces
                    text = text.replace(':', '').replace(' ', '')
                    
                    # Ensure even number of characters for hex conversion
                    if len(text) % 2 != 0:
                        text = '0' + text
                    
                    val_bytes = bytes.fromhex(text)
                    
                    if len(val_bytes) < l:
                        val_bytes += b'\xFF' * (l - len(val_bytes)) # Pad with FF
                    elif len(val_bytes) > l:
                        val_bytes = val_bytes[:l] # Truncate if too long
                    self.data[o:o+l] = val_bytes

                elif key == "Revision" or key == "SKU_Type":
                    text = self.fields[key].get()
                    # Extract the hex part, e.g., "0x01" from "0x01 - Slim"
                    hex_part = text.split(' ')[0] 
                    val = int(hex_part, 16)
                    self.data[o] = val

                elif key == "IDU":
                    text = self.fields[key].get()
                    val = 0xFF if text == "Off" else 0x01
                    self.data[o] = val

                else: # For generic string/hex fields like SN, SOCUID, KIBAN, MB_SN, SKU
                    val_str = self.fields[key].get()
                    info_type = info['t']
                    
                    if info_type == 's': # ASCII string
                        # Pad with FF or truncate to match length
                        val_bytes = val_str.encode('ascii')
                        val_bytes = val_bytes[:l] + b'\xFF' * max(0, l - len(val_bytes))
                        self.data[o:o + l] = val_bytes
                    elif info_type == 'b': # Raw hex bytes 
                        # Ensure even number of characters for hex conversion
                        if len(val_str) % 2 != 0:
                            val_str = '0' + val_str # Prepend '0' if odd length
                        val_bytes = bytes.fromhex(val_str)
                        if len(val_bytes) > l:
                            val_bytes = val_bytes[:l] # Truncate if too long
                        # Pad with FF if too short
                        val_bytes = val_bytes + b'\xFF' * max(0, l - len(val_bytes))
                        self.data[o:o + l] = val_bytes


            with open(file_path, "wb") as f:
                f.write(self.data)
            #messagebox.showinfo("Success", f"Data saved to {file_path} successfully.")
        except ValueError as ve:
            messagebox.showerror("Input Error", f"Validation Error: {ve}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save data: {e}")

    def load_original_file(self):
        """Loads data from the selected original file."""
        if not self.original_file_path:
            messagebox.showerror("Error", "No original file selected.")
            return
        try:
            with open(self.original_file_path, "rb") as f:
                self.data = bytearray(f.read())
            self.populate_fields_from_data()
            ##messagebox.showinfo("Success", "Original file loaded successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load original file: {e}")

    def _apply_raw_config_to_data(self, config_data):
        """
    
        """
        
        max_offset = 0
        for info in self.critical_map.values():
            if info['o'] + info['l'] > max_offset:
                max_offset = info['o'] + info['l']

        
        self.data = bytearray(max_offset) 

        for key, raw_val in config_data.items():
            info = self.critical_map[key]
            o = info['o']
            l = info['l']
            typ = info['t']

            if o + l > len(self.data):
                print(f"Warning: Pre-config value for {key} out of bounds for data buffer. Skipping.")
                continue

            try:
                if typ == 'b': # Byte data (Active_Slot, MODEL, MODEL2, IDU, MACs)
                    if key in ["Active_Slot", "MODEL", "MODEL2", "IDU", "Revision", "SKU_Type"]: # Added Revision and SKU_Type here
                        # Single byte hex string
                        self.data[o] = int(raw_val, 16)
                    elif key.endswith("MAC"): # MAC addresses
                        mac_bytes = bytes.fromhex(raw_val)
                        self.data[o:o+l] = mac_bytes
                elif typ == 's': # String data
                    if key in ["BOARD_ID", "MB_SN", "KIBAN", "REGION", "SKU"]:
                        # Convert hex string to bytes
                        val_bytes = bytes.fromhex(raw_val)
                    elif key in ["SN", "SOCUID"]: # Direct ASCII string from template
                        val_bytes = raw_val.encode('ascii')
                        # When loading from pre-config, we fill with nulls, not FF, as these are *source* bytes
                        val_bytes = val_bytes[:l] + b'\x00' * max(0, l - len(val_bytes)) 
                    else:
                        # Fallback for other string types if any
                        val_bytes = raw_val.encode('ascii')
                        val_bytes = val_bytes[:l] + b'\x00' * max(0, l - len(val_bytes))
                    
                    self.data[o:o+l] = val_bytes
            except Exception as e:
                print(f"Error applying pre-config for {key} with value '{raw_val}': {e}")

    def load_pre_config_values(self, event=None):
        """Loads selected pre-configured values into the GUI fields and internal data."""
        selected_config_name = self.pre_config_combobox.get()
        if not selected_config_name or selected_config_name == "Select a configuration":
            return

        config_data = self.pre_configs.get(selected_config_name)
        if config_data:
            self._apply_raw_config_to_data(config_data) 
            self.populate_fields_from_data() 
           # #messagebox.showinfo("Success", f"Pre-configured values for '{selected_config_name}' loaded successfully.")
        else:
            messagebox.showerror("Error", "Selected pre-configuration not found.")

    def populate_fields_from_data(self):
        """Populates the GUI fields with data read from the loaded file."""
        # First, ensure SKU is populated as REGION depends on it
        sku_info = self.critical_map['SKU']
        sku_offset = sku_info['o']
        sku_length = sku_info['l']
        try:
            if sku_offset + sku_length > len(self.data):
                sku_val_bytes = bytearray(sku_length)
            else:
                sku_val_bytes = self.data[sku_offset:sku_offset + sku_length]
            
            sku_str = ""
            try:
                # When populating from data, if it's primarily an ASCII field, try to decode first
                sku_str = sku_val_bytes.decode('ascii').rstrip('\x00')
            except UnicodeDecodeError:
                # If it fails, fallback to hex representation for display
                sku_str = sku_val_bytes.hex().upper() # Convert to upper for consistency
            
            self.fields['SKU'].delete(0, tk.END)
            self.fields['SKU'].insert(0, sku_str)
        except Exception as e:
            print(f"Error parsing SKU: {e}")
            sku_str = "" # Ensure sku_str is defined even on error

        for key, info in self.critical_map.items():
            offset = info['o']
            length = info['l']

            try:
                # Skip SKU as it's handled separately at the beginning
                if key == "SKU":
                    continue

                val_bytes = None # Initialize to None
                # Ensure we don't try to read beyond the data length for other fields
                if offset + length > len(self.data):
                    val_bytes = bytearray(length) # Create empty bytes if out of bounds
                else:
                    val_bytes = self.data[offset:offset + length]
                
                # Clear existing content in the field
                if isinstance(self.fields[key], ttk.Combobox):
                    self.fields[key].set("")
                else:
                    self.fields[key].delete(0, tk.END)

                # If the read bytes are less than expected, it means data is incomplete
                if val_bytes is None or len(val_bytes) < length: # Check val_bytes for None too
                    # Leave field empty or set to a default 'N/A'
                    continue

                if key == "Active_Slot":
                    raw_val = val_bytes[0]
                    display_val = f"0x{raw_val:02X} - {self.active_slot_map.get(raw_val, 'Unknown')}"
                    self.fields[key].set(display_val)

                elif key == "BOARD_ID":
                    display_val = val_bytes.hex().upper()
                    self.fields[key].insert(0, display_val)

                elif key == "EthernetMAC" or key.startswith("WLAN_MAC") or key.startswith("BD_MAC"):
                    mac_str = ':'.join(f"{b:02X}" for b in val_bytes)
                    self.fields[key].insert(0, mac_str)

                elif key == "Revision":
                    raw_val = val_bytes[0]
                    model_str = self.model_variant_1.get(raw_val, f"Unknown (0x{raw_val:02X})")
                    display_val = f"0x{raw_val:02X} - {model_str}"
                    self.fields[key].set(display_val)

                elif key == "SKU_Type":
                    raw_val = val_bytes[0]
                    model2_str = self.model_variant_2.get(raw_val, f"Unknown (0x{raw_val:02X})")
                    display_val = f"0x{raw_val:02X} - {model2_str}"
                    self.fields[key].set(display_val)

                elif key == "REGION":
                    # Extract region code from SKU string as per user's request
                    region_code = ""
                    # Ensure SKU string is long enough to contain the region code (e.g., "CFI-1102A 01" needs at least 8 chars for index 6 and 7)
                    if len(sku_str) >= 8: 
                        region_code = sku_str[6:8] # Extract "02" from "CFI-1102A 01" example
                    
                    region_name = self.regions.get(region_code, "Unknown")
                    combo_val = f"{region_code} - {region_name}"
                    self.fields[key].set(combo_val)

                elif key == "IDU":
                    raw_val = val_bytes[0]
                    display_val = "Off" if raw_val == 0xFF else "On"
                    self.fields[key].set(display_val)

                else:
                    try:
                        # Attempt to decode as ASCII, removing nulls
                        str_val = val_bytes.decode('ascii').rstrip('\x00')
                        # If the string contains only FF bytes, represent as hex instead of garbage ASCII
                        if all(b == 0xFF for b in val_bytes):
                             str_val = val_bytes.hex().upper()
                    except UnicodeDecodeError: # Catch specific error for decoding issues
                        str_val = val_bytes.hex().upper() # Fallback to hex if not ASCII
                    self.fields[key].insert(0, str_val)

            except Exception as e:
                print(f"Error parsing {key}: {e}") # Print error to console for debugging

            # Configure column weights for data_frame to allow entry/combobox to expand
        self.data_frame.grid_columnconfigure(1, weight=1)

        # --- Footer for QR Code and Thank You message ---
        #self.footer_frame = ttk.Frame(self, padding=(10, 5), relief="flat")
        #self.footer_frame.pack(fill='x', side='bottom', padx=10, pady=(5, 10))
        #self.footer_frame.grid_columnconfigure(0, weight=1) # Center the text and QR code

        # "Thank You!" text
        #thank_you_label = ttk.Label(self.footer_frame, text="Thank You!",
        #                             font=('Inter', 10, 'bold'), foreground="#E0E0E0", background=self.style.lookup("TFrame", "background"))
        #thank_you_label.grid(row=0, column=0, pady=(5, 0), sticky='s')

        # Load and display QR code image
        #try:
            # Construct the path to the QR code image
        #    script_dir = os.path.dirname(__file__) # Get the directory of the current script
        #    qr_path = os.path.join(script_dir, 'data', 'qr.png')

        #    self.qr_image_pil = Image.open(qr_path)
        #    self.qr_image_pil = self.qr_image_pil.resize((80, 80), Image.Resampling.LANCZOS)  # Resize for UI, use Resampling.LANCZOS for quality
        #    self.qr_image_tk = ImageTk.PhotoImage(self.qr_image_pil)
        #    qr_label = ttk.Label(self.footer_frame, image=self.qr_image_tk, background=self.style.lookup("TFrame", "background"))
        #    qr_label.grid(row=1, column=0, pady=(5, 0), sticky='n') # pady between text and image
        #except FileNotFoundError:
        #    messagebox.showwarning("Image Error", f"QR code image not found at: {qr_path}")
        #    # Optional: Display a placeholder or simply omit the QR code label
        #    qr_label = ttk.Label(self.footer_frame, text="QR Code Missing", foreground="red", background=self.style.lookup("TFrame", "background"))
        #    qr_label.grid(row=1, column=0, pady=(5, 0))
        #except Exception as e:
        #    messagebox.showwarning("Image Error", f"Could not load QR code image: {e}")
        #    qr_label = ttk.Label(self.footer_frame, text="QR Code Error", foreground="red", background=self.style.lookup("TFrame", "background"))
        #    qr_label.grid(row=1, column=0, pady=(5, 0))
        # --- End of Footer modifications ---

    def open_harvest_selection_dialog(self):
        """Opens a dialog for the user to select which fields to harvest."""
        dialog = tk.Toplevel(self)
        dialog.title("Select Fields to Harvest")
        dialog.transient(self) # Make dialog transient to main window
        dialog.grab_set() # Make dialog modal
        dialog.focus_set()

        # Center the dialog
        self.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

        dialog_frame = ttk.Frame(dialog, padding=10)
        dialog_frame.pack(fill='both', expand=True)

        self.harvest_checkbox_vars = {}
        # Initialize all checkboxes to True (selected) by default
        for idx, (key, info) in enumerate(self.critical_map.items()):
            var = tk.BooleanVar(value=True)
            cb = ttk.Checkbutton(dialog_frame, text=info['n'], variable=var, style="TCheckbutton")
            cb.grid(row=idx // 2, column=idx % 2, sticky='w', padx=5, pady=2) # Arrange in 2 columns
            self.harvest_checkbox_vars[key] = var

        # Control buttons
        button_frame = ttk.Frame(dialog, padding=10)
        button_frame.pack(fill='x', pady=10)

        ttk.Button(button_frame, text="Select All", command=lambda: self.toggle_all_harvest_checkboxes(True)).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Deselect All", command=lambda: self.toggle_all_harvest_checkboxes(False)).pack(side='left', padx=5)
        ttk.Button(button_frame, text="OK", command=lambda: self.on_harvest_selection_ok(dialog)).pack(side='right', padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side='right', padx=5)

        # Wait until the dialog is closed
        self.wait_window(dialog)

    def toggle_all_harvest_checkboxes(self, state):
        """Toggles the state of all harvest selection checkboxes."""
        for var in self.harvest_checkbox_vars.values():
            var.set(state)

    def on_harvest_selection_ok(self, dialog):
        """Processes the selected fields from the harvest dialog."""
        self.selected_harvest_fields.clear()
        for key, var in self.harvest_checkbox_vars.items():
            if var.get():
                self.selected_harvest_fields.add(key)
        dialog.destroy()
        self.harvest_from_file() # Proceed with harvesting after selection

    def harvest_from_file(self):
        """Harvests critical data from a selected file and updates the current data."""
        if not self.harvest_file_path:
            messagebox.showerror("Error", "No harvest file selected.")
            return
        if not self.data:
            messagebox.showerror("Error", "Load the original file first.")
            return
        if not self.selected_harvest_fields:
            messagebox.showinfo("Info", "No fields selected for harvesting. Operation cancelled.")
            return

        try:
            with open(self.harvest_file_path, "rb") as f:
                harvest_data = bytearray(f.read())

            # Only harvest fields that were selected in the dialog
            for key in self.selected_harvest_fields:
                info = self.critical_map[key]
                o = info['o']
                l = info['l']
                # Only harvest if the harvest_data has enough bytes for the field
                if o + l <= len(harvest_data):
                    self.data[o:o + l] = harvest_data[o:o + l]
                else:
                    print(f"Warning: Harvest file too small for {key}. Skipping harvest for this field.")

            self.populate_fields_from_data()
            #messagebox.showinfo("Success", "Harvested data from file successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to harvest data: {e}")

if __name__ == "__main__":
    app = CriticalInfoApp()
    app.mainloop()