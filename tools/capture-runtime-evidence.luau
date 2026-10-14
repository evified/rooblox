local HS=game:GetService("HttpService")
local out={engine=version(),capturedAt=DateTime.now():ToIsoDate(),services={},scripts={},ui={}}
local function value(v)
 if typeof(v)=="Color3"then return {v.R,v.G,v.B} elseif typeof(v)=="Vector2"then return {v.X,v.Y} elseif typeof(v)=="Vector3"then return {v.X,v.Y,v.Z} elseif typeof(v)=="UDim2"then return {v.X.Scale,v.X.Offset,v.Y.Scale,v.Y.Offset} elseif typeof(v)=="EnumItem"then return tostring(v) elseif typeof(v)=="Font"then return {family=v.Family,weight=tostring(v.Weight),style=tostring(v.Style)} elseif typeof(v)=="Instance"then return v:GetFullName()else return v end
end
local tc=game:GetService("TextChatService")
for _,name in ipairs({"ChatWindowConfiguration","ChatInputBarConfiguration","ChannelTabsConfiguration","BubbleChatConfiguration"})do local o=tc:FindFirstChild(name) if o then local t={}for _,k in ipairs({"Enabled","BackgroundColor3","BackgroundTransparency","TextColor3","TextSize","TextStrokeTransparency","FontFace","WidthScale","HeightScale","KeyboardKeyCode","PlaceholderColor3","AutocompleteEnabled","HoverBackgroundColor3","SelectedTabTextColor3","BubbleDuration","MaxBubbles","MaxDistance","MinimizeDistance","VerticalStudsOffset"})do local ok,v=pcall(function()return o[k]end)if ok then t[k]=value(v)end end out.services[name]=t end end
for _,p in ipairs(game:GetService("Players"):GetPlayers())do
 local scripts=p:FindFirstChild("PlayerScripts")
 if scripts then for _,s in ipairs(scripts:GetDescendants())do if s:IsA("LuaSourceContainer")and(s.Name=="Keyboard"or s.Name=="BaseCamera"or s.Name=="ClassicCamera"or s.Name=="MouseLockController"or s.Name=="ZoomController"or s.Name=="Poppercam"or s.Name=="CameraInput"or s.Name=="ControlModule")then local ok,source=pcall(function()return s.Source end) if ok then out.scripts[s.Name]=source end end end end
end
local cg=game:GetService("CoreGui")
for _,o in ipairs(cg:GetDescendants())do
 if o:IsA("GuiObject")and(o.Name:lower():find("chat")or o.Name:lower():find("topbar")or o.Name:lower():find("menu"))then
 local t={path=o:GetFullName(),class=o.ClassName,name=o.Name}for _,k in ipairs({"AbsolutePosition","AbsoluteSize","Visible","BackgroundColor3","BackgroundTransparency","Image","ImageRectOffset","ImageRectSize","Text","TextSize","FontFace"})do local ok,v=pcall(function()return o[k]end)if ok then t[k]=value(v)end end table.insert(out.ui,t)
 end
end
return HS:JSONEncode(out)
