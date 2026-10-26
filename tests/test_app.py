import unittest
from urllib.parse import urlparse, parse_qs
import flet as ft
from main import main, maps_url


class FakePage:
    width = 1200
    def add(self, *controls): self.controls = list(controls)
    def update(self): pass
    def show_dialog(self, dialog): self.dialog = dialog
    def pop_dialog(self): self.dialog = None


def walk(control):
    yield control
    for child in getattr(control, 'controls', []) or []:
        yield from walk(child)
    content = getattr(control, 'content', None)
    if isinstance(content, ft.Control):
        yield from walk(content)


class UrlTests(unittest.TestCase):
    def test_unicode_and_special_characters(self):
        value = 'Museo & café, Bogotá #1'
        url = maps_url('search', query=value)
        self.assertEqual(urlparse(url).netloc, 'www.google.com')
        self.assertEqual(parse_qs(urlparse(url).query)['query'], [value])
        self.assertEqual(parse_qs(urlparse(url).query)['api'], ['1'])

    def test_route_mode(self):
        url = maps_url('dir', origin='A', destination='B', travelmode='transit')
        self.assertEqual(parse_qs(urlparse(url).query)['travelmode'], ['transit'])

    def test_long_url_rejected(self):
        with self.assertRaises(ValueError): maps_url('search', query='á' * 400)

    def test_action_rejected(self):
        with self.assertRaises(ValueError): maps_url('redirect', query='A')


class InterfaceTests(unittest.TestCase):
    def setUp(self):
        self.page = FakePage()
        main(self.page)

    def all(self):
        return [c for root in self.page.controls for c in walk(root)]

    def button(self, text):
        return next(c for c in self.all() if isinstance(c, (ft.Button, ft.TextButton, ft.OutlinedButton))
                    and c.content == text)

    def field(self, label):
        return next(c for c in self.all() if isinstance(c, ft.TextField) and c.label == label)

    def text_exists(self, text):
        return any(isinstance(c, ft.Text) and c.value == text for c in self.all())

    def test_empty_place_and_stale_link(self):
        field = self.field('Lugar, dirección o coordenadas')
        self.button('Generar búsqueda').on_click(None)
        self.assertFalse(self.button('Abrir lugar en Maps').disabled)
        field.value = ''
        field.on_change(None)
        self.assertTrue(self.button('Abrir lugar en Maps').disabled)
        self.button('Generar búsqueda').on_click(None)
        self.assertIsNotNone(field.error)

    def test_route_validation(self):
        self.field('Origen').value = ' Bogotá '
        self.field('Destino').value = 'bogotá'
        self.button('Generar ruta').on_click(None)
        self.assertTrue(self.button('Abrir ruta en Maps').disabled)
        self.assertIsNotNone(self.field('Destino').error)

    def test_swap_invalidates(self):
        self.button('Generar ruta').on_click(None)
        old = self.field('Origen').value
        self.button('Intercambiar origen y destino').on_click(None)
        self.assertEqual(self.field('Destino').value, old)
        self.assertTrue(self.button('Abrir ruta en Maps').disabled)

    def test_mode_change_invalidates(self):
        self.button('Generar ruta').on_click(None)
        mode = next(c for c in self.all() if isinstance(c, ft.Dropdown))
        mode.value = 'driving';mode.on_select(None)
        self.assertTrue(self.button('Abrir ruta en Maps').disabled)
        self.button('Generar ruta').on_click(None)
        self.assertIn('travelmode=driving', self.button('Abrir ruta en Maps').url.url)

    def test_history_deduplicates_and_caps(self):
        field = self.field('Lugar, dirección o coordenadas')
        for i in range(12):
            field.value = f'Museo {i}';self.button('Generar búsqueda').on_click(None)
        self.assertTrue(self.text_exists('10 de 10 enlaces guardados'))
        self.button('Generar búsqueda').on_click(None)
        self.assertTrue(self.text_exists('10 de 10 enlaces guardados'))
        self.assertTrue(self.text_exists('13 enlaces generados'))

    def test_history_restore_and_clear(self):
        field = self.field('Lugar, dirección o coordenadas')
        field.value = 'Cartagena';self.button('Generar búsqueda').on_click(None)
        field.value = 'Otro lugar';field.on_change(None)
        self.button('Reutilizar').on_click(None)
        self.assertEqual(field.value, 'Cartagena')
        self.assertTrue(self.button('Abrir lugar en Maps').disabled)
        self.button('Vaciar historial').on_click(None)
        self.assertIsNotNone(self.page.dialog)
        self.page.dialog.actions[0].on_click(None)
        self.assertTrue(self.text_exists('1 de 10 enlaces guardados'))
        self.button('Vaciar historial').on_click(None)
        self.page.dialog.actions[1].on_click(None)
        self.assertTrue(self.text_exists('0 de 10 enlaces guardados'))
        self.assertTrue(self.text_exists('1 enlace generado'))

    def test_length_validation(self):
        field = self.field('Lugar, dirección o coordenadas')
        field.value = 'a' * 301;self.button('Generar búsqueda').on_click(None)
        self.assertIsNotNone(field.error)
        self.assertTrue(self.button('Abrir lugar en Maps').disabled)


if __name__ == '__main__':
    unittest.main()
