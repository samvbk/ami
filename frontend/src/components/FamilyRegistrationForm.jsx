// frontend/src/components/FamilyRegistrationForm.jsx
import { useState } from 'react';
import { UserPlus, Trash2, Save } from 'lucide-react';

export default function FamilyRegistrationForm({ onSubmit, onCancel }) {
  const [familyName, setFamilyName] = useState('');
  const [members, setMembers] = useState([{ name: '', role: '', age: '' }]);

  const addMember = () => {
    setMembers([...members, { name: '', role: '', age: '' }]);
  };

  const removeMember = (index) => {
    if (members.length > 1) {
      const newMembers = [...members];
      newMembers.splice(index, 1);
      setMembers(newMembers);
    }
  };

  const updateMember = (index, field, value) => {
    const newMembers = [...members];
    newMembers[index][field] = value;
    setMembers(newMembers);
  };

  const handleSubmit = () => {
    if (!familyName.trim()) {
      alert('Please enter family name');
      return;
    }

    const validMembers = members.filter(m => m.name.trim() !== '');
    if (validMembers.length === 0) {
      alert('Please add at least one family member');
      return;
    }

    onSubmit({
      family_name: familyName,
      members: validMembers
    });
  };

  return (
    <div className="max-w-3xl mx-auto p-8 bg-white/10 backdrop-blur-sm rounded-3xl border border-white/20">
      <h2 className="text-2xl font-bold text-white mb-6">Register New Family</h2>
      
      <div className="space-y-6">
        {/* Family Name */}
        <div>
          <label className="block text-gray-300 mb-2">Family Name</label>
          <input
            type="text"
            value={familyName}
            onChange={(e) => setFamilyName(e.target.value)}
            className="w-full p-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:border-blue-400"
            placeholder="Enter your family name (e.g., Sharma Family)"
          />
        </div>

        {/* Members */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-bold text-white">Family Members</h3>
            <button
              onClick={addMember}
              className="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg flex items-center gap-2"
            >
              <UserPlus className="w-4 h-4" />
              Add Member
            </button>
          </div>

          <div className="space-y-4">
            {members.map((member, index) => (
              <div key={index} className="p-4 bg-white/5 rounded-xl border border-white/10">
                <div className="flex items-center justify-between mb-4">
                  <h4 className="text-white font-medium">Member {index + 1}</h4>
                  {members.length > 1 && (
                    <button
                      onClick={() => removeMember(index)}
                      className="p-1 text-red-400 hover:text-red-300"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  )}
                </div>
                
                <div className="grid md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-gray-300 text-sm mb-1">Name</label>
                    <input
                      type="text"
                      value={member.name}
                      onChange={(e) => updateMember(index, 'name', e.target.value)}
                      className="w-full p-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-400"
                      placeholder="Full name"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-gray-300 text-sm mb-1">Role</label>
                    <select
                      value={member.role}
                      onChange={(e) => updateMember(index, 'role', e.target.value)}
                      className="w-full p-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:border-blue-400"
                    >
                      <option value="">Select Role</option>
                      <option value="Father">Father</option>
                      <option value="Mother">Mother</option>
                      <option value="Son">Son</option>
                      <option value="Daughter">Daughter</option>
                      <option value="Grandparent">Grandparent</option>
                      <option value="Other">Other</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-gray-300 text-sm mb-1">Age</label>
                    <input
                      type="number"
                      value={member.age}
                      onChange={(e) => updateMember(index, 'age', e.target.value)}
                      className="w-full p-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-400"
                      placeholder="Age"
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Buttons */}
        <div className="flex justify-end gap-4 pt-6 border-t border-white/20">
          <button
            onClick={onCancel}
            className="px-6 py-3 border border-white/30 text-white rounded-xl hover:bg-white/10"
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            className="px-6 py-3 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-xl hover:from-green-600 hover:to-emerald-700 flex items-center gap-2"
          >
            <Save className="w-5 h-5" />
            Register Family
          </button>
        </div>
      </div>
    </div>
  );
}