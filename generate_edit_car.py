import codecs
import re

with codecs.open('templates/vehicles/admin/add_car.html', 'r', 'utf-8') as f:
    text = f.read()

text = text.replace('Add New Car', 'Edit Car')
text = text.replace('Enter vehicle details and technical specifications', 'Update vehicle details and technical specifications')
text = text.replace("{% url 'car_add' %}", "{% url 'car_edit' car.id %}")
text = text.replace('id="carAddForm"', 'id="carEditForm"')

inputs = ['make', 'model', 'year', 'min_price', 'max_price', 'mileage', 'engine_displacement', 'max_power', 'max_torque', 'fuel_tank_capacity', 'seating_capacity', 'boot_space']

for field in inputs:
    text = re.sub(f'name="{field}"', f'name="{field}" value="{{{{ car.{field} |default:\'\' }}}}"', text)

js_select_setter = '''
<script>
document.addEventListener('DOMContentLoaded', () => {
  const form = document.querySelector('form');
  if (form) {
    if ('{{ car.body_type }}') form.querySelector('select[name="body_type"]').value = '{{ car.body_type }}';
    if ('{{ car.engine }}') form.querySelector('select[name="engine"]').value = '{{ car.engine }}';
    if ('{{ car.transmission }}') form.querySelector('select[name="transmission"]').value = '{{ car.transmission }}';
    if ('{{ car.safety_rating }}') form.querySelector('select[name="safety_rating"]').value = '{{ car.safety_rating }}';
    
    if ('{{ car.has_sunroof }}' === 'True') form.querySelector('input[name="has_sunroof"]').checked = true;
    else form.querySelector('input[name="has_sunroof"]').checked = false;
    if ('{{ car.has_airbags }}' === 'True') form.querySelector('input[name="has_airbags"]').checked = true;
    else form.querySelector('input[name="has_airbags"]').checked = false;
    if ('{{ car.has_abs }}' === 'True') form.querySelector('input[name="has_abs"]').checked = true;
    else form.querySelector('input[name="has_abs"]').checked = false;
  }
});
</script>
'''

text = text.replace('</form>', js_select_setter + '</form>')
text = re.sub(r'(<textarea name="description".*?>).*?(</textarea>)', r'\1{{ car.description|default:"" }}\2', text, flags=re.DOTALL)

existing_gallery_html = '''
              {% if car.gallery_images.exists %}
              <div style="margin-top: 15px; margin-bottom: 25px;">
                <label style="font-size:14px; font-weight:600; color:#475569;">Existing Gallery Images:</label>
                <div style="display:flex; flex-wrap:wrap; gap:15px; margin-top:10px;">
                  {% for img in car.gallery_images.all %}
                  <div class="gallery-preview-card" style="box-shadow: none; border: 1px solid #e2e8f0; position:relative;">
                    <img src="{{ img.image.url }}" alt="Gallery Image" style="width:100%; height:100%; object-fit:cover;">
                    <span class="preview-tag">{{ img.get_category_display }}</span>
                  </div>
                  {% endfor %}
                </div>
              </div>
              <hr style="border:none; border-top:1px dashed #cbd5e1; margin-bottom:20px;">
              {% endif %}
'''

text = text.replace('<!-- Dropzone -->', existing_gallery_html + '\n              <!-- Dropzone -->')
text = text.replace('Save Vehicle & Upload Options', 'Update Vehicle & Upload Options')
text = text.replace("carForm = document.getElementById('carAddForm')", "carForm = document.querySelector('form')")

with codecs.open('templates/vehicles/admin/edit_car.html', 'w', 'utf-8') as f:
    f.write(text)

print('edit_car.html generated successfully.')
