from dearpygui import dearpygui as dpg

def clicar():
    dpg.set_value('texto', 'Botão clicado!')


dpg.create_context()
dpg.create_viewport(title='Exemplo', width=400, height=200)

with dpg.window(label='Janela'):
    dpg.add_text('Olá, Dear PyGui!', tag='texto')
    dpg.add_button(label='Clique aqui', callback=clicar)


dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
