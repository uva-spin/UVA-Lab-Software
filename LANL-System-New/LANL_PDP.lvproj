<?xml version='1.0' encoding='UTF-8'?>
<Project Type="Project" LVVersion="25008000">
	<Property Name="NI.LV.All.SaveVersion" Type="Str">25.0</Property>
	<Property Name="NI.LV.All.SourceOnly" Type="Bool">true</Property>
	<Property Name="varPersistentID:{023DA9DE-3264-44D7-B704-B0DD4EABE23F}" Type="Ref">/My Computer/Controls.lvlib/Tank RF</Property>
	<Property Name="varPersistentID:{0C398E75-0EB7-4764-ADBC-1C81CC378B5B}" Type="Ref">/My Computer/Controls.lvlib/IF Offset (V)</Property>
	<Property Name="varPersistentID:{19BE046D-6E2F-4D9C-A1FD-9CEF06485C5A}" Type="Ref">/My Computer/Controls.lvlib/Gain</Property>
	<Property Name="varPersistentID:{26677819-9E74-4FC5-A471-4D17AEAAD500}" Type="Ref">/My Computer/Controls.lvlib/Tune (V)</Property>
	<Property Name="varPersistentID:{335197FC-2BB5-4F10-A8F2-7923F1A1327B}" Type="Ref">/My Computer/Controls.lvlib/IF LOG Digitizer</Property>
	<Property Name="varPersistentID:{74540078-BBAE-4298-93A4-6FBCE8075D20}" Type="Ref">/My Computer/Controls.lvlib/Phase (V)</Property>
	<Property Name="varPersistentID:{7EA8092D-6EE2-4BA8-B164-73C439D0A204}" Type="Ref">/My Computer/Controls.lvlib/RF Level OK</Property>
	<Property Name="varPersistentID:{A0CE4CA1-3861-4602-B1F7-F1F69B8B96FE}" Type="Ref">/My Computer/Controls.lvlib/RF Level</Property>
	<Property Name="varPersistentID:{AA6BACE9-0701-48D2-AE8B-BDF4DB21B0D7}" Type="Ref">/My Computer/Controls.lvlib/Frequency Span (MHz)</Property>
	<Property Name="varPersistentID:{DBBA6C50-9A0F-460F-8C87-8CC109E908D2}" Type="Ref">/My Computer/Controls.lvlib/Invert Polarity</Property>
	<Property Name="varPersistentID:{E21017CA-6A48-4CA2-9426-7156A6DEE2D5}" Type="Ref">/My Computer/Controls.lvlib/Step Width (MHz)</Property>
	<Property Name="varPersistentID:{ED5020DC-4147-4D39-BF59-B381FF356063}" Type="Ref">/My Computer/Controls.lvlib/Tune?</Property>
	<Property Name="varPersistentID:{EF6E3F47-D950-4D5C-B3D0-88211511B21D}" Type="Ref">/My Computer/Controls.lvlib/AutoTune</Property>
	<Property Name="varPersistentID:{F32864A6-A040-4CFE-B582-F04CDB19C8B1}" Type="Ref">/My Computer/Controls.lvlib/Frequency Span (kHz)</Property>
	<Property Name="varPersistentID:{F3CA6908-D2DC-44A9-9C82-2507659251F5}" Type="Ref">/My Computer/Controls.lvlib/Center Frequency (MHz)</Property>
	<Item Name="My Computer" Type="My Computer">
		<Property Name="server.app.propertiesEnabled" Type="Bool">true</Property>
		<Property Name="server.control.propertiesEnabled" Type="Bool">true</Property>
		<Property Name="server.tcp.enabled" Type="Bool">false</Property>
		<Property Name="server.tcp.port" Type="Int">0</Property>
		<Property Name="server.tcp.serviceName" Type="Str">My Computer/VI Server</Property>
		<Property Name="server.tcp.serviceName.default" Type="Str">My Computer/VI Server</Property>
		<Property Name="server.vi.callsEnabled" Type="Bool">true</Property>
		<Property Name="server.vi.propertiesEnabled" Type="Bool">true</Property>
		<Property Name="specify.custom.address" Type="Bool">false</Property>
		<Item Name="Controls.lvlib" Type="Library" URL="../Controls/Controls.lvlib"/>
		<Item Name="FM.vi" Type="VI" URL="../Controls/RF/FM.vi"/>
		<Item Name="FT.lvlib" Type="Library" URL="../FT/FT.lvlib"/>
		<Item Name="Gainsel.vi" Type="VI" URL="../Gainsel.vi"/>
		<Item Name="main.vi" Type="VI" URL="../main.vi"/>
		<Item Name="Netburner.lvlib" Type="Library" URL="../Netburner/Netburner.lvlib"/>
		<Item Name="NMR_mods.vi" Type="VI" URL="../../LANL-System/rssmt/NMR_mods.vi"/>
		<Item Name="Untitled 4.vi" Type="VI" URL="../Controls/RF/Untitled 4.vi"/>
		<Item Name="Untitled Library 1.lvlib" Type="Library" URL="../Controls/Tune/Untitled Library 1.lvlib"/>
		<Item Name="Dependencies" Type="Dependencies"/>
		<Item Name="Build Specifications" Type="Build"/>
	</Item>
</Project>
