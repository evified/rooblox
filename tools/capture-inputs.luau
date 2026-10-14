local HS=game.HttpService local out={bindings={},scripts={},settings={}}
local function val(v)if typeof(v)=="Vector2"then return {v.X,v.Y}elseif typeof(v)=="Vector3"then return {v.X,v.Y,v.Z}elseif typeof(v)=="EnumItem"then return tostring(v)else return v end end
for _,o in ipairs(game:GetDescendants())do
 if o:IsA("InputBinding")or o:IsA("InputAction")then local e={path=o:GetFullName(),name=o.Name,class=o.ClassName}for _,k in ipairs({"Scale","Vector2Scale","KeyCode","KeyCodeSecondary","KeyCodeTertiary","KeyCodeQuaternary","UIDirection","Vector2Direction","BoolDirection","InputType","Type","Enabled"})do local ok,v=pcall(function()return o[k]end)if ok then e[k]=val(v)end end table.insert(out.bindings,e)end
 if o:IsA("LuaSourceContainer")and(o.Name=="ActionController"or o.Name=="TransparencyController"or o.Name=="CameraUtils"or o.Name=="DynamicThumbstick"or o.Name=="TouchJump")then local ok,src=pcall(function()return o.Source end)if ok then out.scripts[o.Name]=src end end
end
local u=UserSettings():GetService("UserGameSettings")for _,k in ipairs({"MouseSensitivity","ComputerMovementMode","ComputerCameraMovementMode","RotationType","ControlMode","TouchCameraMovementMode"})do local ok,v=pcall(function()return u[k]end)if ok then out.settings[k]=val(v)end end
return HS:JSONEncode(out)
